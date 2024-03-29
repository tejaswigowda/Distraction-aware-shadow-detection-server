import numpy as np
import os

import torch
from PIL import Image
from torch.autograd import Variable
from torchvision import transforms

from config import sbu_testing_root
from misc import check_mkdir, crf_refine
from model import DSDNet
import sys
# torch.cuda.set_device(0)

ckpt_path = './ckpt'
# exp_name = 'DSA_fuse_data_MYBCE3_try4'
exp_name='models'

args = {
    'snapshot': '5000_SBU',
    'scale': 320
}

img_transform = transforms.Compose([
    transforms.Resize((args['scale'],args['scale'])),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

to_test = {'sbu': sbu_testing_root}

to_pil = transforms.ToPILImage()


def main():
    net = DSDNet()#.cuda()

    if len(args['snapshot']) > 0:
        print('load snapshot \'%s\' for testing' % args['snapshot'])
        net.load_state_dict(torch.load(os.path.join(ckpt_path, exp_name, args['snapshot'] + '.pth')))

    net.eval()
    with torch.no_grad():
        for name, root in to_test.items():
            img_list = [img_name for img_name in os.listdir(root) if
                        img_name.endswith('.jpg')]
            for idx, img_name in enumerate(img_list):
                print('predicting for %s: %d / %d' % (name, idx + 1, len(img_list)))
                check_mkdir(
                    os.path.join('Output/SBU', '%s_%s_prediction_%s' % (exp_name, name, args['snapshot'])))
                img = Image.open(os.path.join(root, img_name))
                w, h = img.size
                img_var = Variable(img_transform(img).unsqueeze(0)).cpu()
                res = net(img_var)
                prediction = np.array(transforms.Resize((h, w))(to_pil(res.data.squeeze(0).cpu())))
                prediction = crf_refine(np.array(img.convert('RGB')), prediction)

                Image.fromarray(prediction).save(
                    os.path.join('Output/SBU', '%s_%s_prediction_%s' % (
                        exp_name, name, args['snapshot']), img_name[:-4])+'.png')


if __name__ == '__main__':
    main()
