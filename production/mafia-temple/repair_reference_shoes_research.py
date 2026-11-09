"""Research-only 2-D footwear replacement for an already-public reference.

Only the generic shoe asset is published. The resulting image can contain a
recognizable person: it must stay in private scratch storage, never be committed
or sent to a public relay. This approximate image edit is a model-conditioning
experiment, not a validated result or a foot-contact solution.
"""
import cv2
import numpy as np


def replace_shoes(reference, generic):
    frame = cv2.resize(reference, (832, 448), interpolation=cv2.INTER_AREA)
    if generic is None or generic.shape[2] != 4:
        raise ValueError('Expected generic RGBA shoe asset')
    specs = [
        ([[296,354],[310,352],[323,361],[325,401],[310,402],[298,394]],
         (310,377), (55,23), (308,352), -55),
        ([[444,390],[460,385],[501,391],[503,406],[453,418],[443,409]],
         (473,402), (50,21), (456,389), 8),
    ]
    for vertices, center, size, anchor, angle in specs:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(vertices, dtype=np.int32)], 255)
        # Borrow adjacent stone as a simple initial-frame patch; inspect output.
        # This is not a geometry-aware background reconstruction.
        source = np.roll(frame, 40, axis=1)
        frame = cv2.seamlessClone(source, frame, mask, center, cv2.NORMAL_CLONE)
        shoe = cv2.resize(generic, size, interpolation=cv2.INTER_AREA)
        ax, ay = round(size[0] * .25), round(size[1] * .22)
        transform = cv2.getRotationMatrix2D((ax, ay), angle, 1.)
        transform[:, 2] += [anchor[0] - ax, anchor[1] - ay]
        warped = cv2.warpAffine(shoe, transform, (832, 448))
        alpha = cv2.GaussianBlur(warped[:, :, 3].astype(np.float32) / 255,
                                 (3, 3), .35)[:, :, None]
        color = warped[:, :, :3].astype(np.float32) * .50
        frame = np.clip(frame * (1 - alpha) + color * alpha, 0, 255).astype(np.uint8)
    return frame
