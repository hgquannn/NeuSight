import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import sys
import torch
import subprocess

def cuda_rr():
  idx = cuda_rr.cuda_idx % cuda_rr.device_num
  cuda_rr.cuda_idx += 1
  return "cuda:"+str(idx)
cuda_rr.cuda_idx = 0
cuda_rr.device_num = torch.cuda.device_count()

jobs = []

def launch_task(model_name, mode, batch_size, seqlen, device, option="", blocking=True):
    p = subprocess.Popen(
        [
            "python3", "../pred.py",
            "--predictor_name", "micro",
            "--predictor_path", "./data/predictor/MICRO",
            "--device_config_path", f"./data/device_configs/{device}.json",
            "--model_config_path", f"./data/DLmodel_configs/{model_name}.json",
            "--sequence_length", str(seqlen),
            "--batch_size", str(batch_size),
            "--execution_type", mode,
            "--tile_dataset_dir", "",
            "--result_dir", "./results",
            "--options", option,
            "--running_device", cuda_rr(),
        ],
        stdout=sys.stdout, 
        stderr=sys.stdout, 
    )

    if blocking:
        p.wait()

    jobs.append(p)

def pred():

    launch_task(model_name="bert_large", mode="inf", batch_size=8, seqlen=512, device="NVIDIA_A100-PCIE-40GB", blocking=False)

    # main inference
    for device in ["NVIDIA_H100_80GB_HBM3", "NVIDIA_A100-PCIE-40GB", "Tesla_T4", "Tesla_V100-PCIE-32GB", "Tesla_P100-PCIE-16GB", "Tesla_P4", "NVIDIA_L4",]:
        launch_task(model_name="bert_large", mode="inf", batch_size=8, seqlen=512, device=device, blocking=False)
        launch_task(model_name="bert_large", mode="inf", batch_size=16, seqlen=512, device=device, blocking=False)
        launch_task(model_name="gpt2_large", mode="inf", batch_size=4, seqlen=1024, device=device, blocking=False)
        launch_task(model_name="gpt2_large", mode="inf", batch_size=8, seqlen=1024, device=device, blocking=False)
        launch_task(model_name="gpt3_xl", mode="inf", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_xl", mode="inf", batch_size=8, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="opt_13", mode="inf", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="opt_13", mode="inf", batch_size=8, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_27", mode="inf", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_27", mode="inf", batch_size=8, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="switchxl4", mode="inf", batch_size=1, seqlen=512, device=device, blocking=False)
        launch_task(model_name="switchxl4", mode="inf", batch_size=2, seqlen=512, device=device, blocking=False)

    for p in jobs:
        p.wait()

    # main train
    for device in ["NVIDIA_H100_80GB_HBM3", "NVIDIA_A100_80GB_PCIe", "Tesla_V100-PCIE-32GB", "NVIDIA_L4",]:
        launch_task(model_name="bert_large", mode="train", batch_size=2, seqlen=512, device=device, blocking=False)
        launch_task(model_name="bert_large", mode="train", batch_size=8, seqlen=512, device=device, blocking=False)
        launch_task(model_name="gpt2_large", mode="train", batch_size=1, seqlen=1024, device=device, blocking=False)
        launch_task(model_name="gpt2_large", mode="train", batch_size=4, seqlen=1024, device=device, blocking=False)
        launch_task(model_name="gpt3_xl", mode="train", batch_size=1, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_xl", mode="train", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="opt_13", mode="train", batch_size=1, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="opt_13", mode="train", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_27", mode="train", batch_size=1, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="gpt3_27", mode="train", batch_size=2, seqlen=2048, device=device, blocking=False)
        launch_task(model_name="switchxl4", mode="train", batch_size=1, seqlen=512, device=device, blocking=False)
        launch_task(model_name="switchxl4", mode="train", batch_size=2, seqlen=512, device=device, blocking=False)

    for p in jobs:
        p.wait()

def main():
    pred()

try:
    main()
except Exception as e:
    print(e)
    for p in jobs:
        p.kill()