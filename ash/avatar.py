"""Draws Ash as an SVG robot: a screen face with seven expressions and two animated arms."""

from itertools import count

GLOW = "#5ee7ff"
SECONDS_PER_MOVE = 0.45
LEFT_SHOULDER, RIGHT_SHOULDER = (85, 198), (235, 198)
_render_ids = count()

# Each face is SVG drawn inside the head's screen. Eyes sit at x=125 and x=195.
FACES = {
    "neutral": '<g class="eyes"><circle cx="125" cy="85" r="13"/><circle cx="195" cy="85" r="13"/></g>'
               '<path d="M140 128 H180"/>',
    "happy": '<path d="M112 90 Q125 72 138 90 M182 90 Q195 72 208 90"/>'
             '<path d="M135 118 Q160 142 185 118"/>',
    "sad": '<g class="eyes"><circle cx="125" cy="90" r="11"/><circle cx="195" cy="90" r="11"/></g>'
           '<path d="M138 135 Q160 117 182 135"/>',
    "listening": '<g class="eyes"><circle cx="125" cy="85" r="17"/><circle cx="195" cy="85" r="17"/></g>'
                 '<circle cx="160" cy="128" r="7" fill="none"/>',
    "thinking": '<g class="eyes"><circle cx="132" cy="77" r="11"/><circle cx="202" cy="77" r="11"/></g>'
                '<path d="M146 130 H170"/><g class="dots"><circle cx="204" cy="128" r="3"/>'
                '<circle cx="214" cy="122" r="3"/><circle cx="224" cy="116" r="3"/></g>',
    "speaking": '<g class="eyes"><circle cx="125" cy="85" r="13"/><circle cx="195" cy="85" r="13"/></g>'
                '<ellipse class="talk" cx="160" cy="126" rx="16" ry="10"/>',
    "error": '<path d="M115 75 L135 95 M135 75 L115 95 M185 75 L205 95 M205 75 L185 95"/>'
             '<path d="M136 130 L146 122 L156 130 L166 122 L176 130 L184 124"/>',
}


def arm_rotation(angle, side):
    """Map a servo angle (135 = down, 45 = up) to an SVG rotation for one arm."""
    degrees = 10 if angle is None else 10 + (135 - angle) * 1.4
    return degrees if side == "left" else -degrees


def _arm_animation(name, side, poses):
    """CSS keyframes that move one arm through the poses and back to rest."""
    index = 0 if side == "left" else 1
    angles = [None, *(pose[index] for pose in poses), None]
    frames = " ".join(
        f"{i * 100 / (len(angles) - 1):.1f}% {{ transform: rotate({arm_rotation(a, side):.0f}deg) }}"
        for i, a in enumerate(angles)
    )
    duration = SECONDS_PER_MOVE * (len(angles) - 1)
    return f"@keyframes {name} {{ {frames} }}", f"animation: {name} {duration:.2f}s ease-in-out;"


def render(face="neutral", poses=()):
    """Return HTML for Ash with the given face, playing the gesture poses once."""
    uid = f"ash-{next(_render_ids)}"
    css = []
    for side, (x, y) in (("left", LEFT_SHOULDER), ("right", RIGHT_SHOULDER)):
        rule = f"transform-origin: {x}px {y}px; transform: rotate({arm_rotation(None, side)}deg);"
        if poses:
            keyframes, animation = _arm_animation(f"{uid}-{side}", side, poses)
            css.append(keyframes)
            rule += animation
        css.append(f"#{uid} .{side} {{ transform-box: view-box; {rule} }}")

    return f"""
<div id="{uid}" class="ash-avatar">
<style>
  {" ".join(css)}
  #{uid} .face {{ stroke: {GLOW}; stroke-width: 7; stroke-linecap: round; fill: none; }}
  #{uid} .face circle, #{uid} .face ellipse {{ fill: {GLOW}; }}
  #{uid} .eyes {{ transform-box: fill-box; transform-origin: center; animation: {uid}-blink 4s infinite; }}
  #{uid} .talk {{ transform-box: fill-box; transform-origin: center; animation: {uid}-talk 0.3s infinite alternate; }}
  #{uid} .dots {{ animation: {uid}-pulse 1s infinite alternate; }}
  #{uid} .light {{ animation: {uid}-pulse 2s infinite alternate; }}
  @keyframes {uid}-blink {{ 0%, 94%, 100% {{ transform: scaleY(1) }} 97% {{ transform: scaleY(0.1) }} }}
  @keyframes {uid}-talk {{ from {{ transform: scaleY(0.3) }} to {{ transform: scaleY(1.1) }} }}
  @keyframes {uid}-pulse {{ from {{ opacity: 0.35 }} to {{ opacity: 1 }} }}
</style>
<svg viewBox="0 -20 320 340" role="img" aria-label="Ash looking {face}">
  <line x1="160" y1="20" x2="160" y2="-2" stroke="#3a4656" stroke-width="6"/>
  <circle class="light" cx="160" cy="-6" r="8" fill="{GLOW}"/>
  <g class="left"><rect x="75" y="190" width="20" height="95" rx="10" fill="#4b596b"/>
    <circle cx="85" cy="290" r="13" fill="#5d6d82"/></g>
  <g class="right"><rect x="225" y="190" width="20" height="95" rx="10" fill="#4b596b"/>
    <circle cx="235" cy="290" r="13" fill="#5d6d82"/></g>
  <rect x="145" y="165" width="30" height="22" fill="#2b3440"/>
  <rect x="95" y="180" width="130" height="120" rx="24" fill="#3a4656"/>
  <circle class="light" cx="160" cy="235" r="10" fill="{GLOW}"/>
  <rect x="60" y="20" width="200" height="150" rx="28" fill="#2b3440"/>
  <rect x="75" y="35" width="170" height="120" rx="18" fill="#0b1320"/>
  <g class="face">{FACES.get(face, FACES["neutral"])}</g>
</svg>
</div>"""
