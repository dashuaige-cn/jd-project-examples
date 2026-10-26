#!/usr/bin/env python3
"""Render every PDF page, in order, into one readable vertical JPEG."""
from __future__ import annotations

import argparse
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps
from pypdf import PdfReader


MIN_WIDTH = 1200
MAX_WIDTH = 4096
MAX_PAGES = 40
MAX_PIXELS = 100_000_000
MAX_HEIGHT = 60_000  # JPEG dimensions must stay below the format's limit.
QUALITIES = (94, 92, 90, 88, 85)


class ExportError(Exception):
    pass


def find_pdftoppm(explicit: str | None) -> str:
    candidates = [explicit, os.environ.get("PDFTOPPM"), shutil.which("pdftoppm")]
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
    candidates.extend([
        str(runtime / "native/poppler/Library/bin/pdftoppm.exe"),
        str(runtime / "native/poppler/bin/pdftoppm"),
    ])
    if explicit:
        resolved = shutil.which(explicit) or explicit
        if not Path(resolved).is_file():
            raise ExportError("指定的 pdftoppm 不存在。")
        return str(resolved)
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise ExportError("未找到 Poppler pdftoppm；请安装或通过 --pdftoppm 指定路径。")


def inspect_pdf(pdf: Path, width: int, gap: int) -> tuple[int, list[int]]:
    if not pdf.is_file():
        raise ExportError("输入 PDF 不存在。")
    if pdf.stat().st_size > 64 * 1024 * 1024:
        raise ExportError("PDF 超过 64 MB，拒绝处理异常大的简历文件。")
    try:
        reader = PdfReader(str(pdf))
        if reader.is_encrypted:
            raise ExportError("请提供未加密的 PDF。")
        count = len(reader.pages)
        if not 1 <= count <= MAX_PAGES:
            raise ExportError(f"页数应为 1 至 {MAX_PAGES} 页。")
        heights = []
        for page in reader.pages:
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            if int(page.rotation or 0) % 180:
                w, h = h, w
            if not all(math.isfinite(v) and v > 0 for v in (w, h)):
                raise ExportError("PDF 包含无效页面尺寸。")
            heights.append(math.ceil(width * h / w))
        check_dimensions(width, sum(heights) + gap * (count - 1))
        return count, heights
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError("PDF 无法读取或页面结构无效。") from exc


def check_dimensions(width: int, height: int) -> None:
    if height < 1 or height > MAX_HEIGHT or width * height > MAX_PIXELS:
        raise ExportError("完整长图将超过尺寸或像素上限；请减少 PDF 页数，不会截掉页面。")


def render_pages(pdf: Path, directory: Path, executable: str, width: int, count: int) -> list[Path]:
    # Explicit page selection preserves ordering even when there are 10+ pages.
    paths = []
    for index in range(1, count + 1):
        prefix = directory / f"page-{index:04d}"
        command = [executable, "-f", str(index), "-l", str(index), "-singlefile",
                   "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
                   str(pdf), str(prefix)]
        try:
            result = subprocess.run(command, check=False, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=60)
        except subprocess.TimeoutExpired as exc:
            raise ExportError(f"第 {index} 页渲染超时。") from exc
        if result.returncode != 0 or not prefix.with_suffix(".png").is_file():
            raise ExportError(f"第 {index} 页渲染失败，未输出不完整长图。")
        paths.append(prefix.with_suffix(".png"))
    return paths


def rgb_page(file: Path, width: int) -> Image.Image:
    try:
        with Image.open(file) as source:
            source.load()
            if source.width < 1 or source.height < 1:
                raise ExportError("页面图片尺寸无效。")
            rgba = ImageOps.exif_transpose(source).convert("RGBA")
            page = Image.new("RGB", rgba.size, "white")
            page.paste(rgba, mask=rgba.getchannel("A"))
            rgba.close()
        # Poppler versions can apply page rotation at different scaling stages.
        # Resize both dimensions proportionally; never stretch or crop content.
        if page.width != width:
            height = max(1, round(page.height * width / page.width))
            resized = page.resize((width, height), Image.Resampling.LANCZOS)
            page.close()
            page = resized
        return page
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError("页面渲染图片不可读。") from exc


def atomic_publish(data: bytes, output: Path, force: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise ExportError("输出文件已存在；要更新该文件请显式使用 --force。")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".resume-image-", suffix=".jpg",
                                         dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        with Image.open(temporary) as image:
            image.verify()
        if force:
            os.replace(temporary, output)
        elif os.name == "nt":
            # Windows rename fails if the destination exists, including races.
            os.rename(temporary, output)
        else:
            # Same-filesystem link atomically publishes without overwriting.
            os.link(temporary, output)
    except FileExistsError as exc:
        raise ExportError("输出文件已存在，未覆盖。") from exc
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def export(pdf: Path, output: Path, *, width: int = 1600, gap: int = 18,
           max_mb: float = 8, pdftoppm: str | None = None, force: bool = False) -> dict:
    pdf, output = pdf.expanduser().resolve(), output.expanduser().resolve()
    if pdf == output:
        raise ExportError("输出不能覆盖源 PDF。")
    if output.suffix.lower() not in (".jpg", ".jpeg"):
        raise ExportError("输出文件必须使用 .jpg 或 .jpeg 扩展名。")
    if not MIN_WIDTH <= width <= MAX_WIDTH:
        raise ExportError(f"为保证文字可读，宽度须为 {MIN_WIDTH} 至 {MAX_WIDTH} 像素。")
    if not 0 <= gap <= 200:
        raise ExportError("页间距须为 0 至 200 像素。")
    if not math.isfinite(max_mb) or not 0 < max_mb <= 100:
        raise ExportError("--max-mb 须大于 0 且不超过 100。")
    if output.exists() and not force:
        raise ExportError("输出文件已存在；要更新该文件请显式使用 --force。")
    count, _ = inspect_pdf(pdf, width, gap)
    executable = find_pdftoppm(pdftoppm)
    max_bytes = int(max_mb * 1024 * 1024)
    with tempfile.TemporaryDirectory(prefix="resume-image-") as temporary:
        paths = render_pages(pdf, Path(temporary), executable, width, count)
        heights = []
        for file in paths:
            with rgb_page(file, width) as page:
                heights.append(page.height)
        height = sum(heights) + gap * (count - 1)
        check_dimensions(width, height)
        with Image.new("RGB", (width, height), "white") as result:
            y = 0
            for file, page_height in zip(paths, heights):
                with rgb_page(file, width) as page:
                    result.paste(page, (0, y))
                y += page_height + gap
            assert y - gap == height
            encoded = None
            selected_quality = None
            for quality in QUALITIES:
                buffer = io.BytesIO()
                result.save(buffer, format="JPEG", quality=quality,
                            subsampling=0, optimize=True, progressive=True)
                if buffer.tell() <= max_bytes:
                    encoded, selected_quality = buffer.getvalue(), quality
                    break
            if encoded is None:
                raise ExportError("完整长图在可读画质下仍超过文件大小限制；请提高 --max-mb，不会压缩成难以阅读的小图。")
    with Image.open(io.BytesIO(encoded)) as image:
        image.load()
        if image.format != "JPEG" or image.mode != "RGB" or image.size != (width, height):
            raise ExportError("长图完整性检查失败。")
    atomic_publish(encoded, output, force)
    return {"path": str(output), "width": width, "height": height,
            "pages": count, "bytes": output.stat().st_size, "quality": selected_quality}


def main() -> int:
    parser = argparse.ArgumentParser(description="将完整 PDF 简历按页序导出为一张高清 JPEG 长图。")
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--gap", type=int, default=18)
    parser.add_argument("--max-mb", type=float, default=8)
    parser.add_argument("--pdftoppm")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        result = export(args.pdf, args.output, width=args.width, gap=args.gap,
                        max_mb=args.max_mb, pdftoppm=args.pdftoppm, force=args.force)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ExportError, OSError) as exc:
        print(f"长图导出失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
