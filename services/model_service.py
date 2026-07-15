from PIL import Image, ImageDraw


def run_placeholder_model(preview_path, result_path):
    """
    这里是模型接口预留位置。

    当前版本：
    - 不调用真实模型
    - 基于 preview 图生成一张模拟异常检测结果图
    - 返回一个示例 abnormality score

    以后接入真实模型时，你只需要把这个函数内部替换成真实推理逻辑。
    """

    image = Image.open(preview_path).convert("RGBA")
    width, height = image.size

    overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    draw.ellipse(
        (
            int(width * 0.56),
            int(height * 0.30),
            int(width * 0.78),
            int(height * 0.52),
        ),
        fill=(65, 152, 172, 110),
        outline=(65, 152, 172, 210),
        width=8,
    )

    draw.ellipse(
        (
            int(width * 0.35),
            int(height * 0.52),
            int(width * 0.52),
            int(height * 0.68),
        ),
        fill=(123, 192, 205, 105),
        outline=(81, 153, 159, 210),
        width=7,
    )

    result = Image.alpha_composite(image, overlay)
    result = result.convert("RGB")
    result.save(result_path)

    return {
        "score": 0.82,
        "status": "completed",
        "message": "Placeholder model completed successfully."
    }


def run_real_model_later(input_path, output_dir):
    """
    以后真实模型接入时，可以参考这个结构。

    例如：
    1. 加载模型
    2. 读取 input_path
    3. 做预处理
    4. 模型推理
    5. 保存 anomaly result image 到 output_dir
    6. 返回 score 和 result_path

    当前阶段不要改这个函数。
    """

    raise NotImplementedError("Real model integration will be added later.")