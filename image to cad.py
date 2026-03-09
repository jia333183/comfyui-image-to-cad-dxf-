"""
ComfyUI Image to CAD (DXF) - 桌面版
功能：将AI图片转换为CAD可打开的DXF文件，并直接保存到桌面
"""
import cv2
import numpy as np
import ezdxf
from ezdxf import colors
import os

class ImageToCADNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("INT", {"default": 128, "min": 0, "max": 255, "step": 1}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("dxf_file_path",)
    FUNCTION = "image_to_cad"
    CATEGORY = "3D"

    def image_to_cad(self, image, threshold, scale):
        # 1. 处理ComfyUI输入的图像数据
        img = image.cpu().numpy()[0]
        img_8bit = (img * 255).astype(np.uint8)  # 转换为0-255的8位图像
        
        # 2. 转为灰度图并二值化
        gray = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2GRAY)
        ret, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
        
        # 3. 提取轮廓（兼容OpenCV 4.x+）
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[-2:]

        # 4. 创建DXF文档
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # 5. 将轮廓绘制为CAD多段线
        for cnt in contours:
            if len(cnt) < 3:
                continue
            points = [(p[0][0] * scale, p[0][1] * scale) for p in cnt]
            msp.add_lwpolyline(
                points,
                close=True,
                dxfattribs={"color": colors.RED, "lineweight": 1}
            )

        # 6. 【核心修改】强制保存到【桌面】
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desktop_path, exist_ok=True)
        dxf_filename = f"cad_output_{os.urandom(4).hex()}.dxf"
        dxf_full_path = os.path.join(desktop_path, dxf_filename)
        
        doc.saveas(dxf_full_path)
        print(f"✅ DXF已保存到桌面: {dxf_full_path}")

        return (dxf_full_path,)

# 节点映射（确保能在ComfyUI中找到）
NODE_CLASS_MAPPINGS = {
    "ImageToCAD_Desktop": ImageToCADNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToCAD_Desktop": "🟢 Image to CAD (桌面版)"
}