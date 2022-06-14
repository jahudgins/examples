import cv2
import numpy

import argparse

def resize(infile_name, outfile_name, max_dim):
    import pdb;pdb.set_trace()
    src = cv2.imread(infile_name)
    # cv2.imshow(infile_name, src)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    shape = numpy.array(src.shape[:2])
    factor = max(shape)
    shape = shape * max_dim / factor
    dim = (shape[1], shape[0])
    
    dst = cv2.resize(src, dim, interpolation=cv2.INTER_LANCZOS4)

    cv2.imwrite(outfile_name, dst)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert file to png with specified max width or height')
    parser.add_argument('--infile', '-i', help='Input filename')
    parser.add_argument('--outfile', '-o', help='Output filename')
    parser.add_argument('--maxdim', '-m', type=int, help='Maximum dimension', default=512)

    args = parser.parse_args()
    resize(args.infile, args.outfile, args.maxdim)
