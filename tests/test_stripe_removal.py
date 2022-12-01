import cupy as cp

from cupy.testing import assert_array_equal, assert_allclose
from mpi4py import MPI

from httomolib.normalisation import normalize_cupy
from httomolib.stripe_removal import remove_stripes_tomocupy, remove_stripe_based_sorting_cupy
from loaders import standard_tomo

comm = MPI.COMM_WORLD


def test_stripe_removal():
    in_file = 'data/tomo_standard.nxs'
    data_key = '/entry1/tomo_entry/data/data'
    image_key = '/entry1/tomo_entry/data/image_key'
    dimension = 1
    preview = [None, None, None]
    pad = 0

    (
        host_data, host_flats, host_darks, _, _, _, _
    ) = standard_tomo(in_file, data_key, image_key, dimension, preview, pad, comm)

    data = cp.asarray(host_data)
    flats = cp.asarray(host_flats)
    darks = cp.asarray(host_darks)
    data = normalize_cupy(data, flats, darks)

    #--- testing the CuPy implementation from TomoCupy ---#
    data_after_stripe_removal = remove_stripes_tomocupy(data)
    for _ in range(10):
        assert_allclose(cp.mean(data_after_stripe_removal), 0.28924704)
        assert_allclose(cp.max(data_after_stripe_removal), 2.715983)
        assert_allclose(cp.min(data_after_stripe_removal), -0.15378489)

    #--- testing the CuPy port of TomoPy's implementation ---#
    corrected_data = remove_stripe_based_sorting_cupy(data)
    for _ in range(10):
        assert_allclose(cp.mean(corrected_data), 0.28907317)
        assert_allclose(cp.max(corrected_data), 2.5370452)
        assert_allclose(cp.min(corrected_data), -0.116429195)
