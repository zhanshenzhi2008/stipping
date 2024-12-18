from stripe_generator import StripeGenerator

def test_basic_functionality():
    try:
        generator = StripeGenerator(400, 300)
        colors = ['#FF0000', '#00FF00', '#0000FF']
        
        # 测试效果1
        img1 = generator.generate_effect1(colors)
        generator.save_png(img1, 'test_effect1')
        
        print("测试成功!")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == '__main__':
    test_basic_functionality() 