# Copyright (c) 2022, Yongqiang Li (yongqiangli@alumni.hust.edu.cn)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
from text.symbols import symbols
import onnxruntime as ort
import torch

from models import SynthesizerTrn
import utils
import time

def to_numpy(tensor):
    return (
        tensor.detach().cpu().numpy()
        if tensor.requires_grad
        else tensor.detach().numpy()
    )


def get_args():
    parser = argparse.ArgumentParser(description="export onnx model")
    parser.add_argument("--checkpoint", required=True, help="checkpoint")
    parser.add_argument("--cfg", required=True, help="config file")
    parser.add_argument("--onnx_model", required=True, help="onnx model")
    parser.add_argument("--phone_table", required=True, help="input phone dict")
    parser.add_argument("--speaker_table", default=None, help="speaker table")
    parser.add_argument(
        "--providers",
        required=False,
        default="CPUExecutionProvider",
        choices=["CUDAExecutionProvider", "CPUExecutionProvider"],
        help="the model to send request to",
    )
    args = parser.parse_args()
    return args


def main():
    os.environ["CUDA_VISIBLE_DEVICES"] = "4"

  
    hps = utils.get_hparams_from_file("./configs/mtl_mts_sdp_character.json")

    phone_num = len(symbols) 
    num_speakers = 8
    
    net_g = SynthesizerTrn(
        phone_num,
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=num_speakers,
        **hps.model
    )
    _ = utils.load_checkpoint("./logs/mtl_mts_sdp_character/G_422000.pth", net_g, None)
    net_g.forward = net_g.export_forward
    net_g.eval()

    seq = torch.randint(low=0, high=phone_num, size=(1, 100), dtype=torch.long)
    seq_len = torch.IntTensor([seq.size(1)]).long()
    scales = torch.FloatTensor([0.667, 1.0, 0.8])
    # make triton dynamic shape happy
    scales = scales.unsqueeze(0)
    sid = torch.IntTensor([1]).long()
    sid_text = torch.IntTensor([1]).long()

    dummy_input = (seq, seq_len, scales, sid, sid_text)
    print("Start export....")
    with torch.cuda.amp.autocast(enabled=True):
      torch.onnx.export(
          model=net_g,
          args=dummy_input,
          f='vits.onnx',
          input_names=["input", "input_lengths", "scales", "sid", "sid_text"],
          output_names=["output"],
          dynamic_axes={
              "input": {0: "batch", 1: "phonemes"},
              "input_lengths": {0: "batch"},
              "scales": {0: "batch"},
              "sid": {0: "batch"},
              "sid_text": {0: "batch"},
              "output": {0: "batch", 1: "audio", 2: "audio_length"},
          },
          opset_version=13,
          verbose=True,
      )

    # Verify onnx precision
    # torch_output = net_g(seq, seq_len, scales, sid)
    # providers = [args.providers]
    # ort_sess = ort.InferenceSession(args.onnx_model, providers=providers)
    # ort_inputs = {
    #     "input": to_numpy(seq),
    #     "input_lengths": to_numpy(seq_len),
    #     "scales": to_numpy(scales),
    #     "sid": to_numpy(sid),
    # }
    # onnx_output = ort_sess.run(None, ort_inputs)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print('Time: ', end-start)
  