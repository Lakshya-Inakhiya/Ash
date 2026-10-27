import pytest

from ash import avatar
from ash.brain import FACES, gesture_poses
from ash.config import load_config


@pytest.mark.parametrize("face", FACES)
def test_every_face_renders(face):
    html = avatar.render(face)
    assert "<svg" in html and avatar.FACES[face] in html


def test_renders_get_unique_ids_so_animations_restart():
    assert avatar.render().split('"')[1] != avatar.render().split('"')[1]


def test_gesture_adds_arm_animation():
    poses = gesture_poses("wave", load_config()["gestures"])
    assert "-left {" not in avatar.render("happy")
    assert "-left {" in avatar.render("happy", poses)


def test_arm_rotation():
    assert avatar.arm_rotation(None, "left") == 10      # resting
    assert avatar.arm_rotation(135, "left") == 10       # servo "down" is resting
    assert avatar.arm_rotation(45, "left") > 90         # servo "up" raises the arm
    assert avatar.arm_rotation(45, "right") == -avatar.arm_rotation(45, "left")
