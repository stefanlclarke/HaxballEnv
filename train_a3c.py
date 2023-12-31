from __future__ import print_function

import os

import torch
import torch.multiprocessing as mp

from haxball_ai.optimizers import my_optim
from haxball_ai.envs import get_2p_env
from haxball_ai.model import ActorCritic
from haxball_ai.test import test
from haxball_ai.train import train
from haxball_ai.settings import settings


if __name__ == '__main__':
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = ""

    torch.manual_seed(settings.seed)
    env = get_2p_env()
    shared_model = ActorCritic(
        env.observation_space.shape[0], env.action_space)
    shared_model.share_memory()

    if settings.no_shared:
        optimizer = None
    else:
        optimizer = my_optim.SharedAdam(shared_model.parameters(), lr=settings.lr)
        optimizer.share_memory()

    processes = []

    counter = mp.Value('i', 0)
    lock = mp.Lock()

    p = mp.Process(target=test, args=(settings.num_processes, settings, shared_model, counter))
    p.start()
    processes.append(p)

    for rank in range(0, settings.num_processes):
        p = mp.Process(target=train, args=(rank, settings, shared_model, counter, lock, optimizer,
                                           settings.steps_per_worker))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
