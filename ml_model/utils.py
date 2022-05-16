import torch
import os
import numpy as np
import json
from torch.utils import data
from tqdm import tqdm
import pandas as pd

from TheOrchidApp import settings


def load_label_map():
    json_path = os.path.join(settings.STATIC_ROOT, "label_map_include.json")
    return json.load(open(json_path))


def get_pt_model_uri():
    path = os.path.join(settings.STATIC_ROOT, "include_no_cnn_transformer_large.pth")
    return path


class KeypointsDataset(data.Dataset):

    def __init__(
            self,
            key_points,
            uid,
            max_frame_len=200,
            frame_length=1080,
            frame_width=1920,
    ):
        self.uid = uid
        self.key_points = key_points
        self.max_frame_len = max_frame_len
        self.frame_length = frame_length
        self.frame_width = frame_width

    def interpolate(self, arr):

        arr_x = arr[:, :, 0]
        arr_x = pd.DataFrame(arr_x)
        arr_x = arr_x.interpolate(method="linear", limit_direction="both").to_numpy()

        arr_y = arr[:, :, 1]
        arr_y = pd.DataFrame(arr_y)
        arr_y = arr_y.interpolate(method="linear", limit_direction="both").to_numpy()

        if np.count_nonzero(~np.isnan(arr_x)) == 0:
            arr_x = np.zeros(arr_x.shape)
        if np.count_nonzero(~np.isnan(arr_y)) == 0:
            arr_y = np.zeros(arr_y.shape)

        arr_x = arr_x * self.frame_width
        arr_y = arr_y * self.frame_length

        return np.stack([arr_x, arr_y], axis=-1)

    def combine_xy(self, x, y):

        x, y = np.array(x), np.array(y)
        _, length = x.shape
        x = x.reshape((-1, length, 1))
        y = y.reshape((-1, length, 1))

        return np.concatenate((x, y), -1).astype(np.float32)

    def __getitem__(self, idx):
        label = self.key_points['label']
        pose = self.combine_xy(self.key_points['pose_x'], self.key_points['pose_y'])
        h1 = self.combine_xy(self.key_points['hand1_x'], self.key_points['hand1_y'])
        h2 = self.combine_xy(self.key_points['hand2_x'], self.key_points['hand2_y'])

        pose = self.interpolate(pose)
        h1 = self.interpolate(h1)
        h2 = self.interpolate(h2)

        df = pd.DataFrame.from_dict(
            {
                "uid": self.key_points['uid'],
                "pose": pose.tolist(),
                "hand1": h1.tolist(),
                "hand2": h2.tolist(),
                "label": label,
            }
        )

        pose = (
            np.array(list(map(np.array, df.pose.values)))
                .reshape(-1, 50)
                .astype(np.float32)
        )
        h1 = (
            np.array(list(map(np.array, df.hand1.values)))
                .reshape(-1, 42)
                .astype(np.float32)
        )
        h2 = (
            np.array(list(map(np.array, df.hand2.values)))
                .reshape(-1, 42)
                .astype(np.float32)
        )
        final_data = np.concatenate((pose, h1, h2), -1)
        final_data = np.pad(
            final_data,
            ((0, self.max_frame_len - final_data.shape[0]), (0, 0)),
            "constant",
        )
        return {
            "uid": self.key_points['uid'],
            "data": torch.FloatTensor(final_data),
        }

    def __len__(self):
        return 1


@torch.no_grad()
def inference(dataloader, model, device, label_map, uid):
    model.eval()
    predictions = []

    for batch in tqdm(dataloader, desc="Eval"):
        input_data = batch["data"].to(device)
        output = model(input_data).detach().cpu()
        output = torch.argmax(torch.softmax(output, dim=-1), dim=-1).numpy()
        predictions.append({'uid': uid, 'predicted_label': label_map[output[0]]})

    return predictions[0]
