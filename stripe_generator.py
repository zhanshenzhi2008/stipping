import os
from PIL import Image, ImageDraw
import svgwrite
import numpy as np
from typing import Tuple, List
import colorsys
import sys

class StripeGenerator:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.current_colors = []
        self.current_stripe_width = 40

    def generate_effect1(self, colors: List[str], angle: float = 45, stripe_width: int = 40) -> Image.Image:
        """生成第一种效果：简单斜条纹"""
        try:
            img = Image.new('RGB', (self.width, self.height), 'white')
            draw = ImageDraw.Draw(img)
            
            offset = stripe_width * 2
            
            for i in range(-self.height, self.height * 2, offset):
                for color in colors:
                    points = [
                        (i, 0),
                        (i + self.height, self.height),
                        (i + self.height + stripe_width, self.height),
                        (i + stripe_width, 0)
                    ]
                    draw.polygon(points, fill=color)
            
            return img.rotate(angle)
        except Exception as e:
            print(f"生成效果1时出错: {e}")
            sys.exit(1)

    def generate_effect2(self, colors: List[str], wave_height: int = 50) -> Image.Image:
        """生成第二种效果：波浪条纹"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        stripe_width = self.width // (len(colors) * 2)
        
        for x in range(0, self.width, stripe_width):
            for i, color in enumerate(colors):
                points = []
                for y in range(0, self.height, 2):
                    offset = int(wave_height * np.sin((y/self.height) * 2 * np.pi))
                    points.append((x + offset, y))
                
                points.extend([(x + stripe_width + offset, y) for y in range(self.height-1, -1, -2)])
                draw.polygon(points, fill=color)
        
        return img

    def generate_effect3(self, base_color: str, num_stripes: int = 10) -> Image.Image:
        """生成第三种效果：渐变条纹"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        # 将hex颜色转换为HSV
        rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
        hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
        stripe_width = self.width // num_stripes
        
        for i in range(num_stripes):
            # 调整饱和度生成渐变
            sat = 0.3 + (0.7 * i / num_stripes)
            rgb = colorsys.hsv_to_rgb(hsv[0], sat, hsv[2])
            color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
            
            points = [
                (i * stripe_width, 0),
                ((i+1) * stripe_width, 0),
                ((i+1) * stripe_width, self.height),
                (i * stripe_width, self.height)
            ]
            draw.polygon(points, fill=color)
        
        return img

    def generate_effect4(self, colors: List[str], spacing: int = 20) -> Image.Image:
        """生成第四种效果：交错条纹"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        for y in range(0, self.height, spacing * 2):
            for i, color in enumerate(colors):
                offset = (i * spacing) % (len(colors) * spacing)
                for x in range(-offset, self.width, len(colors) * spacing):
                    points = [
                        (x, y),
                        (x + spacing, y),
                        (x + spacing, y + spacing),
                        (x, y + spacing)
                    ]
                    draw.polygon(points, fill=color)
        
        return img

    def save_png(self, img: Image.Image, filename: str):
        """保存为PNG格式"""
        if not os.path.exists('output'):
            os.makedirs('output')
        img.save(f'output/{filename}.png')
    
    def save_svg(self, img: Image.Image, filename: str):
        """保存为SVG格式"""
        if not os.path.exists('output'):
            os.makedirs('output')
        
        dwg = svgwrite.Drawing(f'output/{filename}.svg', size=(self.width, self.height))
        
        # 根据不同效果类型优化SVG生成
        if filename == 'effect1':
            # 对于斜条纹，直接生成路径
            for i, color in enumerate(self.current_colors):
                stripe_width = self.current_stripe_width
                offset = stripe_width * 2
                points = [
                    (i * offset, 0),
                    ((i + 1) * offset, 0),
                    ((i + 1) * offset + stripe_width, self.height),
                    (i * offset + stripe_width, self.height)
                ]
                path = dwg.path(d=f'M {points[0][0]},{points[0][1]} L {points[1][0]},{points[1][1]} L {points[2][0]},{points[2][1]} L {points[3][0]},{points[3][1]} Z')
                path.fill(color)
                dwg.add(path)
        else:
            # 对于其他效果，使用优化的像素转换
            rgb_data = img.convert('RGB')
            current_paths = {}
            
            for y in range(0, self.height, 2):
                for x in range(self.width):
                    pixel_color = rgb_data.getpixel((x, y))
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*pixel_color)
                    
                    if hex_color not in current_paths:
                        current_paths[hex_color] = []
                    current_paths[hex_color].append((x, y))
            
            # 合并相邻的相同颜色区域
            for color, points in current_paths.items():
                if points:
                    path_data = []
                    current_group = [points[0]]
                    
                    for point in points[1:]:
                        if point[0] == current_group[-1][0] + 1 and point[1] == current_group[-1][1]:
                            current_group.append(point)
                        else:
                            if len(current_group) > 1:
                                path_data.append(f'M {current_group[0][0]} {current_group[0][1]} H {current_group[-1][0] + 1} V {current_group[0][1] + 2} H {current_group[0][0]} Z')
                            current_group = [point]
                    
                    if current_group:
                        path_data.append(f'M {current_group[0][0]} {current_group[0][1]} H {current_group[-1][0] + 1} V {current_group[0][1] + 2} H {current_group[0][0]} Z')
                    
                    if path_data:
                        path = dwg.path(d=' '.join(path_data))
                        path.fill(color)
                        dwg.add(path)
        
        dwg.save()

def validate_color(color: str) -> bool:
    """验证颜色格式是否正确"""
    if not color.startswith('#'):
        return False
    try:
        int(color[1:], 16)
        return len(color) == 7
    except ValueError:
        return False

def validate_colors(colors: List[str]) -> bool:
    """验证颜色列表"""
    return all(validate_color(color) for color in colors)

def main():
    try:
        print("Python版本:", sys.version)
        print("运行平台:", sys.platform)
        
        generator = StripeGenerator()
        
        while True:
            try:
                print("\n选择效果类型 (1-4):")
                effect_type = int(input().strip())
                if effect_type not in [1, 2, 3, 4]:
                    raise ValueError("效果类型必须是1-4之间的数字")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
            except Exception as e:
                print(f"未知错误: {e}")
        
        # 宽度输入验证
        while True:
            try:
                print("输入图像宽度 (默认800):")
                width = input().strip()
                width = int(width) if width else 800
                if width <= 0:
                    raise ValueError("宽度必须大于0")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
        
        # 高度输入验证
        while True:
            try:
                print("输入图像高度 (默认600):")
                height = input().strip()
                height = int(height) if height else 600
                if height <= 0:
                    raise ValueError("高度必须大于0")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
        
        generator = StripeGenerator(width, height)
        
        # 根据效果类型处理不同的输入
        if effect_type == 1:
            while True:
                try:
                    print("输入条纹颜色 (用逗号分隔的十六进制颜色码，例如: #FF6B6B,#4ECDC4,#45B7D1)")
                    colors = input().strip().split(',') or ['#FF6B6B', '#4ECDC4', '#45B7D1']
                    if not validate_colors(colors):
                        raise ValueError("颜色格式不正确")
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            
            print("输入旋转角度 (默认45):")
            angle = float(input().strip() or 45)
            
            print("输入条纹宽度 (默认40):")
            stripe_width = int(input().strip() or 40)
            
            generator.current_colors = colors  # 保存当前颜色用于SVG生成
            generator.current_stripe_width = stripe_width  # 保存当前条纹宽度
            img = generator.generate_effect1(colors, angle, stripe_width)
            
        elif effect_type == 2:
            while True:
                try:
                    print("输入条纹颜色 (用逗号分隔的十六进制颜色码，例如: #FFD93D,#FF6B6B,#4ECDC4)")
                    colors = input().strip().split(',') or ['#FFD93D', '#FF6B6B', '#4ECDC4']
                    if not validate_colors(colors):
                        raise ValueError("颜色格式不正确")
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            
            print("输入波浪高度 (默认50):")
            wave_height = int(input().strip() or 50)
            
            img = generator.generate_effect2(colors, wave_height)
            
        elif effect_type == 3:
            while True:
                try:
                    print("输入基础颜色 (十六进制颜色码，例如: #FF6B6B)")
                    base_color = input().strip() or '#FF6B6B'
                    if not validate_color(base_color):
                        raise ValueError("颜色格式不正确")
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            
            print("输入条纹数量 (默认10):")
            num_stripes = int(input().strip() or 10)
            
            img = generator.generate_effect3(base_color, num_stripes)
            
        elif effect_type == 4:
            while True:
                try:
                    print("输入条纹颜色 (用逗号分隔的十六进制颜色码，例如: #6C5B7B,#C06C84,#F67280)")
                    colors = input().strip().split(',') or ['#6C5B7B', '#C06C84', '#F67280']
                    if not validate_colors(colors):
                        raise ValueError("颜色格式不正确")
                    break
                except ValueError as e:
                    print(f"输入错误: {e}")
            
            print("输入间距 (默认20):")
            spacing = int(input().strip() or 20)
            
            img = generator.generate_effect4(colors, spacing)
        
        # 输出格式选择
        while True:
            try:
                print("选择输出格式 (1: PNG, 2: SVG, 3: 两种都要):")
                output_format = int(input())
                if output_format not in [1, 2, 3]:
                    raise ValueError("输出格式必须是1-3之间的数字")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
        
        if output_format in (1, 3):
            generator.save_png(img, f'effect{effect_type}')
        if output_format in (2, 3):
            generator.save_svg(img, f'effect{effect_type}')
        
        print(f"图案已保存到 output 目录")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 