"""
ComfyUI Image to CAD (DXF) - 工程图纸专用版
功能：针对黑白线条图优化，提取内部轮廓和边缘，保存到桌面
"""
import cv2
import numpy as np
import ezdxf
from ezdxf import colors
import os

class ImageToCADTechnical:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold1": ("INT", {"default": 50, "min": 0, "max": 255}),
                "threshold2": ("INT", {"default": 150, "min": 0, "max": 255}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("dxf_file_path",)
    FUNCTION = "image_to_cad"
    CATEGORY = "3D"

    def image_to_cad(self, image, threshold1, threshold2, scale):
        # 1. 处理图像数据
        img = image.cpu().numpy()[0]
        img_8bit = (img * 255).astype(np.uint8)
        gray = cv2.cvtColor(img_8bit, cv2.COLOR_RGB2GRAY)

        # 2. 【关键升级】使用Canny边缘检测（专门找线条）
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # 3. 【关键升级】形态学操作，把断开的线条连起来
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        # 4. 查找所有轮廓（包括内部的细小轮廓）
        contours, _ = cv2.findContours(
            edges, cv2.RETR_LIST,  # 改为RETR_LIST，提取所有轮廓
            cv2.CHAIN_APPROX_SIMPLE
        )[-2:]

        # 5. 创建DXF
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # 6. 过滤掉过小的噪点，绘制所有轮廓
        min_length = 10  # 过滤极短的线条
        for cnt in contours:
            if cv2.arcLength(cnt, True) < min_length:
                continue
            points = [(p[0][0] * scale, p[0][1] * scale) for p in cnt]
            if len(points) > 1:
                msp.add_lwpolyline(
                    points,
                    close=False,  # 机械图大多是不闭合的线
                    dxfattribs={"color": colors.GREEN, "lineweight": 1}
                )

        # 7. 保存到桌面
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        dxf_filename = f"technical_drawing_{os.urandom(4).hex()}.dxf"
        dxf_full_path = os.path.join(desktop_path, dxf_filename)
        doc.saveas(dxf_full_path)
        
        print(f"✅ 工程图纸已保存到桌面: {dxf_full_path}")
        return (dxf_full_path,)

NODE_CLASS_MAPPINGS = {
    "ImageToCAD_Technical": ImageToCADTechnical
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToCAD_Technical": "🟢 Image to CAD (工程图纸版)"
}