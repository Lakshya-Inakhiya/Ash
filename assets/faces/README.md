# Face Images for Ash

This directory should contain 7 PNG images (480×320 pixels each) for Ash's facial expressions.

## Required Files

Place the following PNG files in this directory:

1. **happy.png** - Happy/cheerful expression
   - Displayed after giving an answer successfully
   - Should look friendly and satisfied

2. **sad.png** - Sad/empathetic expression
   - Used for empathetic responses
   - Should look concerned or sympathetic

3. **neutral.png** - Neutral/default expression
   - Default idle state
   - Should look calm and ready

4. **listening.png** - Listening/attentive expression
   - Shown while listening for user speech
   - Should look attentive, maybe with emphasized ears or microphone indicator

5. **speaking.png** - Speaking/talking expression
   - Shown while Ash is speaking
   - Maybe with open mouth or sound waves

6. **thinking.png** - Thinking/processing expression
   - Shown while processing with Gemini AI
   - Could have thought bubbles, gears, or contemplative look

7. **error.png** - Error/confused expression
   - Shown when an error occurs
   - Should look confused, worried, or show an error symbol

## Image Specifications

- **Resolution**: 480 × 320 pixels (landscape orientation)
- **Format**: PNG (supports transparency)
- **Color**: RGB or RGBA
- **File naming**: Lowercase, exactly as listed above

## Creating the Images

### Option 1: AI Image Generation

Use an AI image generator with prompts like:

```
"Simple minimalist robot face with [emotion] expression, 
480x320 pixels, flat design, suitable for small LCD screen, 
clean background, friendly and approachable"
```

Recommended tools:
- DALL-E (OpenAI)
- Midjourney
- Stable Diffusion
- Bing Image Creator (free)

### Option 2: Manual Design

Use image editing software:
- Adobe Photoshop
- GIMP (free)
- Figma (free, web-based)
- Canva (free, web-based)

Design tips:
- Keep it simple and clear
- Use high contrast (will be visible on small screen)
- Large features (eyes, mouth) work better
- Avoid fine details that won't show well at 480×320

### Option 3: Emoji-Based Design

Quick and simple approach:
1. Create a 480×320 canvas with solid color background
2. Add large emoji(s) centered
3. Optionally add simple shapes or text
4. Export as PNG

### Option 4: Simple Shapes

Create minimalist faces using:
- Two circles for eyes
- A curve for mouth
- Optional accessories (glasses, antennae, etc.)

Example Python script to create basic faces (using PIL):

```python
from PIL import Image, ImageDraw

def create_face(filename, eye_y, mouth_shape):
    img = Image.new('RGB', (480, 320), color='#2C3E50')
    draw = ImageDraw.Draw(img)
    
    # Eyes
    draw.ellipse([150, eye_y, 200, eye_y+50], fill='white')
    draw.ellipse([280, eye_y, 330, eye_y+50], fill='white')
    draw.ellipse([165, eye_y+15, 185, eye_y+35], fill='black')
    draw.ellipse([295, eye_y+15, 315, eye_y+35], fill='black')
    
    # Mouth (varies by expression)
    if mouth_shape == 'happy':
        draw.arc([180, 200, 300, 280], start=0, end=180, fill='white', width=5)
    elif mouth_shape == 'sad':
        draw.arc([180, 180, 300, 260], start=180, end=360, fill='white', width=5)
    elif mouth_shape == 'neutral':
        draw.line([180, 240, 300, 240], fill='white', width=5)
    
    img.save(filename)

# Create sample faces
create_face('happy.png', 100, 'happy')
create_face('sad.png', 100, 'sad')
create_face('neutral.png', 100, 'neutral')
# ... etc
```

## Testing Your Images

Once you've added all 7 PNG files, test them:

```bash
cd ~/Desktop/Ash-1
python3 src/face_display.py
```

This will cycle through all expressions so you can see how they look on the LCD.

## Tips

- Test on the actual LCD - images may look different on the small screen
- Ensure good contrast for visibility
- Simple is better - complex details get lost
- Keep file sizes reasonable (under 1MB per image)
- Use consistent style across all expressions

## Need Help?

If you need help creating face images:
1. Ask in robotics/Raspberry Pi communities
2. Use free design tools like Canva
3. Commission an artist on Fiverr or similar
4. Start with simple emoji-based designs and improve later

The robot will work perfectly fine with simple designs - personality matters more than artistic perfection!

