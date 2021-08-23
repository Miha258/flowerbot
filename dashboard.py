from PIL import Image, ImageDraw

def draw_progress(image: Image, percent: int):
    
    if percent < 0:
        return image

    if percent > 100:
        percent = 100

    
    progress_width = 429 * (percent / 100)
    progress_height = 78

    x0 = 315
    y0 = 270 
    x1 = x0 + progress_width
    y1 = y0 + progress_height

    
    drawer = ImageDraw.Draw(image,"RGBA")
    drawer.rectangle([(x0,y0),(x1,y1)],fill=(225,225,225))
    
    return image
