import pygame
import json
import os

def load_map_data(map_file):
    with open(map_file, 'r') as f:
        return json.load(f)

def main():
    pygame.init()
    
    # 加载地图数据
    map_data = load_map_data(os.path.join("Resources", "Map1.json"))
    grid_width = map_data['grid_width']
    grid_height = map_data['grid_height']
    rows = map_data['rows']
    cols = map_data['cols']
    layers = map_data['layers']
    
    # 创建Pygame窗口
    screen_width = cols * grid_width
    screen_height = rows * grid_height
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("BomberMan Map")
    
    # 加载图片资源
    images = {}
    for image_name in map_data['image_cache'].values():
        image_path = os.path.join("Resources", image_name)
        images[image_name] = pygame.image.load(image_path)
    
    # 绘制地图
    for layer in layers:
        for row in range(rows):
            for col in range(cols):
                cell = layer['grid_data'][row][col]
                if cell:
                    screen.blit(images[cell], (col * grid_width, row * grid_height))
    
    pygame.display.flip()
    
    # 主循环
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()

if __name__ == '__main__':
    main()
