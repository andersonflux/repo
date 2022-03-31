import shutil
import tempfile
import os

from electrum_mona import constants, blockchain
from electrum_mona.simple_config import SimpleConfig
from electrum_mona.blockchain import Blockchain, deserialize_header, hash_header
from electrum_mona.util import bh2u, bfh, make_dir

from . import ElectrumTestCase


class TestBlockchain(ElectrumTestCase):

    HEADERS = {
        'A': deserialize_header(bfh("0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff7f2002000000"), 0),
        'B': deserialize_header(bfh("0000002006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f186c8dfd970a4545f79916bc1d75c9d00432f57c89209bf3bb115b7612848f509c25f45bffff7f2000000000"), 1),
        'C': deserialize_header(bfh("00000020686bdfc6a3db73d5d93e8c9663a720a26ecb1ef20eb05af11b36cdbc57c19f7ebf2cbf153013a1c54abaf70e95198fcef2f3059cc6b4d0f7e876808e7d24d11cc825f45bffff7f2000000000"), 2),
        'D': deserialize_header(bfh("00000020122baa14f3ef54985ae546d1611559e3f487bd2a0f46e8dbb52fbacc9e237972e71019d7feecd9b8596eca9a67032c5f4641b23b5d731dc393e37de7f9c2f299e725f45bffff7f2000000000"), 3),
        'E': deserialize_header(bfh("00000020f8016f7ef3a17d557afe05d4ea7ab6bde1b2247b7643896c1b63d43a1598b747a3586da94c71753f27c075f57f44faf913c31177a0957bbda42e7699e3a2141aed25f45bffff7f2001000000"), 4),
        'F': deserialize_header(bfh("000000201d589c6643c1d121d73b0573e5ee58ab575b8fdf16d507e7e915c5fbfbbfd05e7aee1d692d1615c3bdf52c291032144ce9e3b258a473c17c745047f3431ff8e2ee25f45bffff7f2000000000"), 5),
        'O': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066526f45bffff7f2001000000"), 6),
        'P': deserialize_header(bfh("00000020abe8e119d1877c9dc0dc502d1a253fb9a67967c57732d2f71ee0280e8381ff0a9690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe28126f45bffff7f2000000000"), 7),
        'Q': deserialize_header(bfh("000000202ce41d94eb70e1518bc1f72523f84a903f9705d967481e324876e1f8cf4d3452148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e1a126f45bffff7f2000000000"), 8),
        'R': deserialize_header(bfh("00000020552755b6c59f3d51e361d16281842a4e166007799665b5daed86a063dd89857415681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221a626f45bffff7f2000000000"), 9),
        'S': deserialize_header(bfh("00000020a13a491cbefc93cd1bb1938f19957e22a134faf14c7dee951c45533e2c750f239dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fab26f45bffff7f2000000000"), 10),
        'T': deserialize_header(bfh("00000020dbf3a9b55dfefbaf8b6e43a89cf833fa2e208bbc0c1c5d76c0d71b9e4a65337803b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064b026f45bffff7f2002000000"), 11),
        'U': deserialize_header(bfh("000000203d0932b3b0c78eccb39a595a28ae4a7c966388648d7783fd1305ec8d40d4fe5fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9db726f45bffff7f2001000000"), 12),
        'G': deserialize_header(bfh("00000020b833ed46eea01d4c980f59feee44a66aa1162748b6801029565d1466790c405c3a141ce635cbb1cd2b3a4fcdd0a3380517845ba41736c82a79cab535d31128066928f45bffff7f2001000000"), 6),
        'H': deserialize_header(bfh("00000020e19e687f6e7f83ca394c114144dbbbc4f3f9c9450f66331a125413702a2e1a719690c2fe7c1a4450c74dc908fe94dd96c3b0637d51475e9e06a78e944a0c7fe26a28f45bffff7f2002000000"), 7),
        'I': deserialize_header(bfh("0000002009dcb3b158293c89d7cf7ceeb513add122ebc3880a850f47afbb2747f5e48c54148be228a4c3f2061bafe7efdfc4a8d5a94759464b9b5c619994d45dfcaf49e16a28f45bffff7f2000000000"), 8),
        'J': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a462555822552221c928f45bffff7f2000000000"), 9),
        'K': deserialize_header(bfh("00000020bb3b421653548991998f96f8ba486b652fdb07ca16e9cee30ece033547cd1a6e9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548fca28f45bffff7f2000000000"), 10),
        'L': deserialize_header(bfh("00000020c391d74d37c24a130f4bf4737932bdf9e206dd4fad22860ec5408978eb55d46303b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe064ca28f45bffff7f2000000000"), 11),
        'M': deserialize_header(bfh("000000206a65f3bdd3374a5a6c4538008ba0b0a560b8566291f9ef4280ab877627a1742815681cb2d00ff889193f6a68a93f5096aeb2d84ca0af6185a4625558225522214229f45bffff7f2000000000"), 9),
        'N': deserialize_header(bfh("00000020383dab38b57f98aa9b4f0d5ff868bc674b4828d76766bf048296f4c45fff680a9dc087fc977b06c24a69c682d1afd1020e6dc1f087571ccec66310a786e1548f4329f45bffff7f2003000000"), 10),
        'X': deserialize_header(bfh("0000002067f1857f54b7fef732cb4940f7d1b339472b3514660711a820330fd09d8fba6b03b243756c25053253aeda309604363460a3911015929e68705bd89dff6fe0649b29f45bffff7f2002000000"), 11),
        'Y': deserialize_header(bfh("00000020db33c9768a9e5f7c37d0f09aad88d48165946c87d08f7d63793f07b5c08c527fd67cb902a7d807cee7676cb543feec3e053aa824d5dfb528d5b94f9760313d9d9b29f45bffff7f2000000000"), 12),
        'Z': deserialize_header(bfh("0000002047822b67940e337fda38be6f13390b3596e4dea2549250256879722073824e7f0f2596c29203f8a0f71ae94193092dc8f113be3dbee4579f1e649fa3d6dcc38c622ef45bffff7f2003000000"), 13),
    }
    # tree of headers:
    #                                            - M <- N <- X <- Y <- Z
    #                                          /
    #                             - G <- H <- I <- J <- K <- L
    #                           /
    # A <- B <- C <- D <- E <- F <- O <- P <- Q <- R <- S <- T <- U

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        constants.set_regtest()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        constants.set_mainnet()

    def setUp(self):
        super().setUp()
        self.data_dir = self.electrum_path
        make_dir(os.path.join(self.data_dir, 'forks'))
        self.config = SimpleConfig({'electrum_path': self.data_dir})
        blockchain.blockchains = {}

    def _append_header(self, chain: Blockchain, header: dict):
        chain.save_header(header)

    def test_get_height_of_last_common_block_with_chain(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_parents_after_forking(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

    def test_forking_and_swapping(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])

        self._append_header(chain_l, self.HEADERS['K'])

        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

#    def test_doing_multiple_swaps_after_single_new_header(self):
#        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
#            config=self.config, forkpoint=0, parent=None,
#            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
#        open(chain_u.path(), 'w+').close()

#        self._append_header(chain_u, self.HEADERS['A'])
#        self._append_header(chain_u, self.HEADERS['B'])
#        self._append_header(chain_u, self.HEADERS['C'])
#        self._append_header(chain_u, self.HEADERS['D'])
#        self._append_header(chain_u, self.HEADERS['E'])
#        self._append_header(chain_u, self.HEADERS['F'])
#        self._append_header(chain_u, self.HEADERS['O'])
#        self._append_header(chain_u, self.HEADERS['P'])
#        self._append_header(chain_u, self.HEADERS['Q'])
#        self._append_header(chain_u, self.HEADERS['R'])
#        self._append_header(chain_u, self.HEADERS['S'])

#        chain_l = chain_u.fork(self.HEADERS['G'])
#        self._append_header(chain_l, self.HEADERS['H'])
#        self._append_header(chain_l, self.HEADERS['I'])
#        self._append_header(chain_l, self.HEADERS['J'])
#        self._append_header(chain_l, self.HEADERS['K'])
#        # now chain_u is best chain, but it's tied with chain_l

#        chain_z = chain_l.fork(self.HEADERS['M'])
#        self._append_header(chain_z, self.HEADERS['N'])
#        self._append_header(chain_z, self.HEADERS['X'])

#        self.assertEqual(3, len(blockchain.blockchains))
#        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))

#        # chain_z became best chain, do checks
#        self.assertEqual(0, chain_z.forkpoint)
#        self.assertEqual(None, chain_z.parent)
#        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
#        self.assertEqual(None, chain_z._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
#        self.assertEqual(12 * 80, os.stat(chain_z.path()).st_size)
#        self.assertEqual(9, chain_l.forkpoint)
#        self.assertEqual(chain_z, chain_l.parent)
#        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
#        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_2874a1277687ab8042eff9916256b860a5b0a08b0038456c5a4a37d3bdf3656a_6e1acd473503ce0ee3cee916ca07db2f656b48baf8968f999189545316423bbb"), chain_l.path())
#        self.assertEqual(2 * 80, os.stat(chain_l.path()).st_size)
#        self.assertEqual(6, chain_u.forkpoint)
#        self.assertEqual(chain_z, chain_u.parent)
#        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
#        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
#        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_5c400c7966145d56291080b6482716a16aa644eefe590f984c1da0ee46ed33b8_aff81830e28e01ef7d23277c56779a6b93f251a2d50dcc09d7c87d119e1e8ab"), chain_u.path())
#        self.assertEqual(5 * 80, os.stat(chain_u.path()).st_size)

#        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
#        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
#        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
#        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
#        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
#        self.assertEqual(hash_header(self.HEADERS['X']), chain_z.get_hash(11))

#        for b in (chain_u, chain_l, chain_z):
#            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

    def get_chains_that_contain_header_helper(self, header: dict):
        height = header['block_height']
        header_hash = hash_header(header)
        return blockchain.get_chains_that_contain_header(height, header_hash)

#    def test_get_chains_that_contain_header(self):
#        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
#            config=self.config, forkpoint=0, parent=None,
#            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
#        open(chain_u.path(), 'w+').close()
#        self._append_header(chain_u, self.HEADERS['A'])
#        self._append_header(chain_u, self.HEADERS['B'])
#        self._append_header(chain_u, self.HEADERS['C'])
#        self._append_header(chain_u, self.HEADERS['D'])
#        self._append_header(chain_u, self.HEADERS['E'])
#        self._append_header(chain_u, self.HEADERS['F'])
#        self._append_header(chain_u, self.HEADERS['O'])
#        self._append_header(chain_u, self.HEADERS['P'])
#        self._append_header(chain_u, self.HEADERS['Q'])

#        chain_l = chain_u.fork(self.HEADERS['G'])
#        self._append_header(chain_l, self.HEADERS['H'])
#        self._append_header(chain_l, self.HEADERS['I'])
#        self._append_header(chain_l, self.HEADERS['J'])
#        self._append_header(chain_l, self.HEADERS['K'])
#        self._append_header(chain_l, self.HEADERS['L'])

#        chain_z = chain_l.fork(self.HEADERS['M'])

#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['A']))
#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['C']))
#        self.assertEqual([chain_l, chain_z, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['F']))
#        self.assertEqual([chain_l, chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['G']))
#        self.assertEqual([chain_l, chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['I']))
#        self.assertEqual([chain_z], self.get_chains_that_contain_header_helper(self.HEADERS['M']))
#        self.assertEqual([chain_l], self.get_chains_that_contain_header_helper(self.HEADERS['K']))

#        self._append_header(chain_z, self.HEADERS['N'])
#        self._append_header(chain_z, self.HEADERS['X'])
#        self._append_header(chain_z, self.HEADERS['Y'])
#        self._append_header(chain_z, self.HEADERS['Z'])

#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['A']))
#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['C']))
#        self.assertEqual([chain_z, chain_l, chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['F']))
#        self.assertEqual([chain_u], self.get_chains_that_contain_header_helper(self.HEADERS['O']))
#        self.assertEqual([chain_z, chain_l], self.get_chains_that_contain_header_helper(self.HEADERS['I']))


class TestVerifyHeader(ElectrumTestCase):

    # Data for Bitcoin block header #100.
    valid_header = "0100000095194b8567fe2e8bbda931afd01a7acd399b9325cb54683e64129bcd00000000660802c98f18fd34fd16d61c63cf447568370124ac5f3be626c2e1c3c9f0052d19a76949ffff001d33f3c25d"
    target = Blockchain.bits_to_target(0x1d00ffff)
    prev_hash = "00000000cd9b12643e6854cb25939b39cd7a1ad0af31a9bd8b2efe67854b1995"

    def setUp(self):
        super().setUp()
        self.header = deserialize_header(bfh(self.valid_header), 100)

    def test_valid_header(self):
        #Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_expected_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target,
        #                             expected_header_hash="foo")
        return

    def test_prev_hash_mismatch(self):
        #with self.assertRaises(Exception):
        #    Blockchain.verify_header(self.header, "foo", self.target)
        return

    def test_target_mismatch(self):
        #with self.assertRaises(Exception):
        #    other_target = Blockchain.bits_to_target(0x1d00eeee)
        #    Blockchain.verify_header(self.header, self.prev_hash, other_target)
        return

    def test_insufficient_pow(self):
        #with self.assertRaises(Exception):
        #    self.header["nonce"] = 42
        #    Blockchain.verify_header(self.header, self.prev_hash, self.target)
        return

    def test_get_target(self):

        # before DGWv3 with checkpoint(height=2015)
        headers1 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2015, headers1)
        self.assertEqual(bits, 65339010432214603900175979833807329994044402934458085644623414103638016)

        # before DGWv3 without checkpoint(height=2016)
        headers2 = {2015: {'version': 2, 'prev_block_hash': 'f9cba205f996e98f61f87e32ae57fc0a5befa6cd632dd257f3e239f390010622', 'merkle_root': 'af68c1f62b965172df1d81fba95f193cb8e42431bad79a4bfbcc370d301d5710', 'timestamp': 1388536705, 'bits': 503936911, 'nonce': 780010496, 'block_height': 2015}}
        bits = Blockchain.get_target(self, 2016, headers2)
        self.assertEqual(bits, 0)

        # after DGWv3 with checkpoint(height=461663)
        headers3 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461663, headers3)
        self.assertEqual(bits, 62635231089126922960074598435273835921110428291665699134377033728)

        # after DGWv3 without checkpoint(height=461664)
        headers4 = {461663: {'version': 3, 'prev_block_hash': '9c87f1e27717aec18617496970b9744dd855f997128fab6733e709fd95d97870', 'merkle_root': '7f22e9001ab92b14a1b057ce07c4f2acecb693f3a645004f36c2246b7ea86c3b', 'timestamp': 1444439492, 'bits': 469801026, 'nonce': 928239, 'block_height': 461663}}
        bits = Blockchain.get_target(self, 461664, headers4)
        self.assertEqual(bits, 0)

        # after DGWv3 after checkpoint(2618875)
        headers5 = {2618784: {'version': 536870912, 'prev_block_hash': '532cb5a56f4c3507cc86f32911ecd0357f84ef8c8ddb51d2ae5da04c9ee0c4e7', 'merkle_root': 'c2f6e50198822ad87f10c91687262715b227b153b388b2ea92b51b06760f7e49', 'timestamp': 1648454687, 'bits': 436439054, 'nonce': 800831806, 'block_height': 2618784}, 2618785: {'version': 536870912, 'prev_block_hash': '47aa5e6c6444eeab3d99ff6152ba4a0cd0cf80158d6740ca356384886a386037', 'merkle_root': '4d749cba817f021b9f5e291d50ba2244e999442090f3ef66ffb03b89aabf3dc3', 'timestamp': 1648454699, 'bits': 436431182, 'nonce': 2061501865, 'block_height': 2618785}, 2618786: {'version': 536870912, 'prev_block_hash': 'ba888947a71a019173b7eb9b65c506c8190097f0b242c82fc56c055727008f55', 'merkle_root': '079c3330d1ab62cd4616d424263c2e531b9350fb7375057da19f1f1b77978746', 'timestamp': 1648454762, 'bits': 436416078, 'nonce': 276875797, 'block_height': 2618786}, 2618787: {'version': 536870912, 'prev_block_hash': '1cb221978e2cca668741551ddcd3d85ee9d7a3e91c9519ef989db3442a120e7f', 'merkle_root': '6a0022e6b29ceaf964f53a09ca2162d1f8b88fea78b32346d2d528d1a2a8dcc0', 'timestamp': 1648454838, 'bits': 436407231, 'nonce': 2501571884, 'block_height': 2618787}, 2618788: {'version': 536870912, 'prev_block_hash': '165344fd2057674c16ddb6d294aaa30e8b9067015bfb11690940ee3c2b0444c7', 'merkle_root': 'bd7f5b3e5d5c776df449f7c2038dfd613a5c0dc30381f1fa74075b5179aee195', 'timestamp': 1648454988, 'bits': 436388556, 'nonce': 1515075197, 'block_height': 2618788}, 2618789: {'version': 536870912, 'prev_block_hash': '6cafc8e95853368a2e08fcabbd33e51893bba6134baa8bfc8446052eb96ab561', 'merkle_root': '8cd06f818d5efa08e5a7e84440d25cc93bce54a96ea12d84c0af3bf6ea55bb4f', 'timestamp': 1648455044, 'bits': 436391147, 'nonce': 2260645445, 'block_height': 2618789}, 2618790: {'version': 536870912, 'prev_block_hash': '234423c031966a6316615de259793418a642b84f2d9705a72762723c48e5bae3', 'merkle_root': 'a5a1f9d72025179e7b53974a543a628eb5bd0f15e02982f40231d8f49031c325', 'timestamp': 1648455131, 'bits': 436385233, 'nonce': 2906645803, 'block_height': 2618790}, 2618791: {'version': 536870912, 'prev_block_hash': 'ae4934eb612543903ce27c6102ab26eaa0add7926d9e9e8c28eb90e56542628e', 'merkle_root': 'cb7d21de7796b39c8907ec30c863b64a2e05c8eb0417babf30fca8baaed51b5c', 'timestamp': 1648455458, 'bits': 436383040, 'nonce': 2300005932, 'block_height': 2618791}, 2618792: {'version': 536870912, 'prev_block_hash': '75e47e26dabc83375f0560ce3e11b08ac132337465cfc4e7aa4894d3fbd87e30', 'merkle_root': '8a4ab946a04e03e003119fb8bf8eae938bdcf26f9e927f859649dad509716217', 'timestamp': 1648455711, 'bits': 436408308, 'nonce': 451907795, 'block_height': 2618792}, 2618793: {'version': 536870912, 'prev_block_hash': '2f83b0a24e3bda32383401975e0ffa3ee9c542140c017e12c23801266b65741c', 'merkle_root': '3494f5de6d38528f6a80937d02d8beb100be1e7f4ef11baa1e0b65e22da3aa65', 'timestamp': 1648456174, 'bits': 436426890, 'nonce': 2230217716, 'block_height': 2618793}, 2618794: {'version': 536870912, 'prev_block_hash': '30f81af05ac6fd261d3829195b384dd6d068a21a53bfa4bdac737be0ef81902e', 'merkle_root': '111ea9fd7c3d3cea6f6d6a10772f4ac68310bef4f2ffe6c12dafa8ae9a46471f', 'timestamp': 1648456226, 'bits': 436467819, 'nonce': 2564742553, 'block_height': 2618794}, 2618795: {'version': 536870912, 'prev_block_hash': 'ebee9d53c5abdfee6f4ea9eef91f6d6f7d4ee2e89926ee9b644615d6743ef135', 'merkle_root': '1c67a1da3f68ebbe816c06245c0597d4be2e62c8db47ceebc37642a8964115d3', 'timestamp': 1648456301, 'bits': 436472977, 'nonce': 1255807378, 'block_height': 2618795}, 2618796: {'version': 536870912, 'prev_block_hash': '8975c72fa0988187bdcf97f53cce035e4fc4b03c22b14938a4d9200360813216', 'merkle_root': 'e551849edc4be3f526ae0d5cce8447d10e48fc6d2f4a186dfced0500365732fe', 'timestamp': 1648456399, 'bits': 436472320, 'nonce': 3480290560, 'block_height': 2618796}, 2618797: {'version': 536870912, 'prev_block_hash': 'd0d4f0fd289c5f76b7f0b6ee90657a74783bd4a554e08a9c1fcc017e36512b63', 'merkle_root': '8c9231a921bb02bc7e2ca4238c85f04be26688e9a04fe4d9f3ef4f52526ef11e', 'timestamp': 1648456548, 'bits': 436468301, 'nonce': 2514076258, 'block_height': 2618797}, 2618798: {'version': 536870912, 'prev_block_hash': 'cd0cf9ea97d2274fa0b227c827dc3428647b497bb724cce2bcb384eabbdff313', 'merkle_root': '6917dbe2e40ca9049e2bdc34fbfa17cf60b7f796d74d093a42efb06fcb7320e4', 'timestamp': 1648456579, 'bits': 436481220, 'nonce': 1695649115, 'block_height': 2618798}, 2618799: {'version': 536870912, 'prev_block_hash': 'b548605338ef370e7bb3801870d700ef40aecc6b6dfc98dda525c477c0197e90', 'merkle_root': 'fd09442ca2bf27b1eadd0b7d41a781d03a708be8ae95b13ebee839e871858569', 'timestamp': 1648456581, 'bits': 436484574, 'nonce': 2854217027, 'block_height': 2618799}, 2618800: {'version': 536870912, 'prev_block_hash': '4fe25e6ab0329179901ecf8c85b8121e31490ec37f6f65308bc3e22d0f455660', 'merkle_root': '50174657b11a0fbf960fdfcff83286c642fe1045dcf234bee3b760a4d38a4ecd', 'timestamp': 1648456643, 'bits': 436481969, 'nonce': 740142859, 'block_height': 2618800}, 2618801: {'version': 536870912, 'prev_block_hash': 'fe524786f6cf63feb9965ac13739218bc7fb87d3356dc616aa7f833a639252f9', 'merkle_root': 'f7fc29f0ad936e950a90024aaa01be9e7845fe468388322ccb628d38246ceb62', 'timestamp': 1648456740, 'bits': 436475599, 'nonce': 2636678409, 'block_height': 2618801}, 2618802: {'version': 536870912, 'prev_block_hash': '34d667357452020491d7c365f3aa9c774c97e7463d176efed72132a444981441', 'merkle_root': '247c6ffaed518e876a5f9fef773af027cc7812de8056344eb75873fc4bfbf758', 'timestamp': 1648456824, 'bits': 436476751, 'nonce': 883981264, 'block_height': 2618802}, 2618803: {'version': 536870912, 'prev_block_hash': '92932b245398acb0ef4187fc0d1cc86009ee2f06706152e19705634a0500578f', 'merkle_root': '794b213f71718ba0b11879cdd504346b744c1ddce54a60f474ee284ba4fea5bb', 'timestamp': 1648456830, 'bits': 436479345, 'nonce': 1490833184, 'block_height': 2618803}, 2618804: {'version': 536870912, 'prev_block_hash': '1632664d2d8e9d664aba419405d122cdef1bab29c7b5399f2c0d6d2c23799b6d', 'merkle_root': '96b87703032f8966c6b74a25f45f14ad0239a0b593da07bf98e05c32e5b5a3f5', 'timestamp': 1648456851, 'bits': 436480073, 'nonce': 3748146612, 'block_height': 2618804}, 2618805: {'version': 536870912, 'prev_block_hash': '189cbc8cc4e4184a45a4bd6afc20b1ea56f10bfd73f3d4be78c3b1313b9b3fec', 'merkle_root': 'e7b13fd83a7dab95b512d05d28058884f81ec7fb63da8eda08d3f6c769cb07a7', 'timestamp': 1648457060, 'bits': 436466223, 'nonce': 1031691898, 'block_height': 2618805}, 2618806: {'version': 536870912, 'prev_block_hash': 'a05dfa617fce08b4f8a4d0d18e04aefc8c29cd543ce8980f370990d1fdb258ee', 'merkle_root': '8a418178b6c0465bb73fa602b4a83572efe607a8d7ec1a36dcd4265c99ed7c74', 'timestamp': 1648457094, 'bits': 436488963, 'nonce': 77225204, 'block_height': 2618806}, 2618807: {'version': 536870912, 'prev_block_hash': '9221403b751a1f9a4acce8eb655a0c952e29c93ce3ab8b6accc7e5266ef0b907', 'merkle_root': 'b42914b21be382378e8f3f886c33a0660a5eadc214694c774ef453229689019a', 'timestamp': 1648457186, 'bits': 436479597, 'nonce': 1904661818, 'block_height': 2618807}, 2618808: {'version': 536870912, 'prev_block_hash': 'be308a0e78b6f3bc5960c9c516d2e17a5cb79566f5b81f16c73aceb4415dcd92', 'merkle_root': '92f0fee8c9ca1f6e3b449ae001a2ddc110ff1d3a96d4df30ab3fe0f41a83d8b3', 'timestamp': 1648457244, 'bits': 436487209, 'nonce': 1623664048, 'block_height': 2618808}, 2618809: {'version': 536870912, 'prev_block_hash': '861f5d85fbf0a6fd5a44ae15545ba374146f864b0328d4e04570ca15cd44e84f', 'merkle_root': 'add67040acbcce4945eb9ebaed6df463c16aac5208c073a2bee8c8ce97eb81f4', 'timestamp': 1648457263, 'bits': 436494984, 'nonce': 1990817566, 'block_height': 2618809}, 2618810: {'version': 536870912, 'prev_block_hash': '7320ce0d6785e4bb9611dd66aee304c760608d8dff6ad62c5e6abda3dc3904d5', 'merkle_root': '300a2b6cf7da30acc54a5830162ef9cfe262e303170f32d0589d7fa91b1e0d17', 'timestamp': 1648457437, 'bits': 436493331, 'nonce': 2683838570, 'block_height': 2618810}, 2618811: {'version': 536870912, 'prev_block_hash': '543c9b3fb01061a4308b0c2d9a9ac3f7c60f26b2a87de59437581133173964f7', 'merkle_root': '877be11308d58e2426b154661f132646e169043cb6e8b0a6e992e0d805d5b40a', 'timestamp': 1648457476, 'bits': 436508165, 'nonce': 2983801929, 'block_height': 2618811}, 2618812: {'version': 536870912, 'prev_block_hash': '080df18c488f5b53956547a14c5c222911b37b9bf8098aa09746ce8fd38870e1', 'merkle_root': '5ff6d8d9f35a2ba823c506bb4c2ec56000ef14eb85685b7ca394d86424bd83df', 'timestamp': 1648457478, 'bits': 436500663, 'nonce': 2407588396, 'block_height': 2618812}, 2618813: {'version': 536870912, 'prev_block_hash': '71fdb3bec4cdb7cc3b1fe953d74c548e494cb4cd5eaf36e130747c62006632a7', 'merkle_root': '074073d631559da99844d02d4a5082ec7da2c6576e10576dc63ed70b323bcb61', 'timestamp': 1648457490, 'bits': 436499018, 'nonce': 87870722, 'block_height': 2618813}, 2618814: {'version': 536870912, 'prev_block_hash': '2d9e8da757931c552b8bee573fe7cccb31176d7a4d95c81b8d1eaaf85952f7b9', 'merkle_root': '683efd12c3c31ceb91f530106d930eb78e121e2d45060c097a1411c998a6e7db', 'timestamp': 1648457505, 'bits': 436494679, 'nonce': 2612564662, 'block_height': 2618814}, 2618815: {'version': 536870912, 'prev_block_hash': '60fc87cec13667d530e007162cd2c5fb9c8a2e7aa87d84ef9ef5fe7e95cc8dd9', 'merkle_root': '76903ca60795848d0de9ccb4167f2256cff50b603a7780b69286de01fba48d6a', 'timestamp': 1648457565, 'bits': 436460697, 'nonce': 4101027857, 'block_height': 2618815}, 2618816: {'version': 536870912, 'prev_block_hash': '370f0cbf611af49794b9f95a1705a479af1eda9acb138e8abd22d6c4359c4576', 'merkle_root': '8f52defa78eaf404e576645094aa46cee0b3c9bd0d016231d42261b9b4a4c6a6', 'timestamp': 1648457650, 'bits': 436438335, 'nonce': 1466486827, 'block_height': 2618816}, 2618817: {'version': 536870912, 'prev_block_hash': '87303635b1d63668e91a931a7666a53d5ad78626af04786ff6bc601979e35f06', 'merkle_root': '819abdcae41495f48b8612d75c9b2a09b5ccfb26a06244e118078ac81ffc26c9', 'timestamp': 1648457691, 'bits': 436391504, 'nonce': 2823143080, 'block_height': 2618817}, 2618818: {'version': 536870912, 'prev_block_hash': '2163e800cfa82c1a755b488fc6ff60b31b26324140f562055527b4fe3f027444', 'merkle_root': '504cbce676461051bbf3ac6e04339752ad4509675cd7b9f4532c79d89c4c0e11', 'timestamp': 1648457902, 'bits': 436387903, 'nonce': 2315422377, 'block_height': 2618818}, 2618819: {'version': 536870912, 'prev_block_hash': 'ca7a9d73dfc5181d8aa3a748450ef7eb534ec97e79157a4f77a3145911bed65e', 'merkle_root': 'f3dd167615f53d8e0e620d179778fae8d2648f1a7a82a22fc449a71c65acbca9', 'timestamp': 1648457909, 'bits': 436402164, 'nonce': 2060966096, 'block_height': 2618819}, 2618820: {'version': 536870912, 'prev_block_hash': 'dda03efeaf59c76c41a533a3a0fe6a6eaa6f721e5aaf28834e85630f18a064e8', 'merkle_root': '902c92511628d0bb8ef53bf1443bd0c9708c5fb73680599081c1b3255777a6c6', 'timestamp': 1648458051, 'bits': 436389524, 'nonce': 1940601491, 'block_height': 2618820}, 2618821: {'version': 536870912, 'prev_block_hash': 'd6c5265e419481cf052cb328055abc64f85d1fdc74a03b865beacf7b64f29e72', 'merkle_root': '810f4ec41037f50ae3d7af3bcd2e7e68abf168c4e3463d61d2fba63fdfeb9b44', 'timestamp': 1648458135, 'bits': 436386025, 'nonce': 2670525697, 'block_height': 2618821}, 2618822: {'version': 536870912, 'prev_block_hash': 'c0e6a60c2d7ccfcfb712b64bf5032ba6f3d364e8a289775aa76f2c98c4c40bb0', 'merkle_root': 'b0c578526733e9304f7c2c51f75eba45bc475a0323032404c6b230d1227f218a', 'timestamp': 1648458184, 'bits': 436389844, 'nonce': 721939884, 'block_height': 2618822}, 2618823: {'version': 536870912, 'prev_block_hash': '99bc54dd7fef5d1542d62d65e62d220b47a19f9bf29f6c5984dbe2951c6aba40', 'merkle_root': '9d3c62347d5fe17b9608d668abcb007d62e69131a281f74f7fb0ebca7b4a3370', 'timestamp': 1648458278, 'bits': 436392750, 'nonce': 1501563153, 'block_height': 2618823}, 2618824: {'version': 536870912, 'prev_block_hash': 'c3edb3520672f2014540a62e17124ebd2b21f085da1e785a7ea6124fae66c94f', 'merkle_root': '1eba04d4ccc0f4dca2d2cd5ff31bfd837db958a666d4fee9a003a5a9d3b8fa71', 'timestamp': 1648458573, 'bits': 436393753, 'nonce': 3346540934, 'block_height': 2618824}, 2618825: {'version': 536870912, 'prev_block_hash': '087950cf0257ff69e09c90a8f4d52d9cfdb5e04b86daf6175a3c3957371499cc', 'merkle_root': '7d240044a5ee3e8b5cf5625bdb11391bd854e764a6746047092f90ad58c104b5', 'timestamp': 1648458737, 'bits': 436413334, 'nonce': 3632796686, 'block_height': 2618825}, 2618826: {'version': 536870912, 'prev_block_hash': 'd1fef461d8ee845bcd5e59a16778d12c23cc6da08c342909c8e0c1d9269b63b9', 'merkle_root': '861bda71d54fd4bf7ad2aa03ebcc3b49b0332face84081a5f6d9d871e405654d', 'timestamp': 1648458831, 'bits': 436420801, 'nonce': 2120247580, 'block_height': 2618826}, 2618827: {'version': 536870912, 'prev_block_hash': 'c1848ee9e87bf23e51084a732a223493eb93f1a0022ef51049138ab9f3b67b3c', 'merkle_root': 'ba447aeb8581c4838a23e40f45a05f9034e8571111fc2ae51d12379667386f3f', 'timestamp': 1648458873, 'bits': 436428811, 'nonce': 3735309405, 'block_height': 2618827}, 2618828: {'version': 536870912, 'prev_block_hash': '87d01320fe5de7bdbd31fb2daa31ec55d8fc58f507575d605d93bf767444866d', 'merkle_root': 'f32862d33a5f3d598573165ece591066dbb955243376d5996b6ef4cfdfe1a0b7', 'timestamp': 1648459310, 'bits': 436429540, 'nonce': 3912983066, 'block_height': 2618828}, 2618829: {'version': 536870912, 'prev_block_hash': '31084a1fa28ceb7e2c9d2b4efcdf0d7edb0d94e02ccf579aef16ae4650540df0', 'merkle_root': 'f4715ff6488e2daaca573c364d01713171721b311cfd3ff5e689005ff4a250ad', 'timestamp': 1648459324, 'bits': 436452489, 'nonce': 2060272107, 'block_height': 2618829}, 2618830: {'version': 536870912, 'prev_block_hash': 'bebf16063e5009fc29e1a365fe113bbf053822b140ec440908d9b2e32de79f7e', 'merkle_root': '0f879d5d2313450473a8ff5a669cf8b604d4f42af80b4b36dd2255f31ae7356f', 'timestamp': 1648459400, 'bits': 436450693, 'nonce': 1171463489, 'block_height': 2618830}, 2618831: {'version': 536870912, 'prev_block_hash': '8f690c54fb0b54b6d0112891283d939158174832573b5f48e1b402634d16b1e3', 'merkle_root': 'e8b185301a1a20ef7b10f7217eb23eed321c8c8a7f76c64361b03829758fe241', 'timestamp': 1648459403, 'bits': 436447306, 'nonce': 1926560881, 'block_height': 2618831}, 2618832: {'version': 536870912, 'prev_block_hash': 'e2974c4453f5976954b70b8063b7cd17221e969f3a065455680ae98a25646af3', 'merkle_root': 'f27e6b20fa2f804538a3d9b40805d831d7f5aed6402e4ce8e2ab99fb9ce6e7d0', 'timestamp': 1648459542, 'bits': 436439925, 'nonce': 679031411, 'block_height': 2618832}, 2618833: {'version': 536870912, 'prev_block_hash': '48de2e2fda36122c2b44bfa261ed9e28fced8f9b97586abc84ef754e31fc88a8', 'merkle_root': '5de9fa455c2a2780ed419a3e0fec37689143c6b2d73826be71a610005632672e', 'timestamp': 1648459563, 'bits': 436450530, 'nonce': 614109764, 'block_height': 2618833}, 2618834: {'version': 536870912, 'prev_block_hash': 'e3de9f26ce7e2caeef0c1420640ab7f7ff10163ac981389f81491c94ba721405', 'merkle_root': 'b4479d23a5c39249d59aa1cb851b3c2b39dce4d76c597cea7bb8f2adf5c709f4', 'timestamp': 1648459677, 'bits': 436432889, 'nonce': 2622140229, 'block_height': 2618834}, 2618835: {'version': 536870912, 'prev_block_hash': 'b6a70f45552d736216ff5ce8550b6089bbdc022b72cf2487fffdaf68f467a26f', 'merkle_root': 'fd8d20a3f0a3663f149842db4c80ab412bc65836b9b256e5a4a102b502755b1a', 'timestamp': 1648460075, 'bits': 436437654, 'nonce': 3087544151, 'block_height': 2618835}, 2618836: {'version': 536870912, 'prev_block_hash': 'a9648ca27d60a66bb57cd3715c6c9fbb8f4eb77978fd2da7e9fa7703361a8898', 'merkle_root': '3f97ecb86b34e451546b783f0fc8a003049e88f18df58f6f44b415575a45fb74', 'timestamp': 1648460289, 'bits': 436475880, 'nonce': 2959248990, 'block_height': 2618836}, 2618837: {'version': 536870912, 'prev_block_hash': 'e736c97c2e7de36c35fbc2ff6a4d0899471b047606b6dc429b8d3eb5f5b0b561', 'merkle_root': 'a8ff12f61481b0a5085243e96917423ebd99ac242d887b68b1486a131d197462', 'timestamp': 1648460391, 'bits': 436497443, 'nonce': 2980060261, 'block_height': 2618837}, 2618838: {'version': 536870912, 'prev_block_hash': '1e0c65499b7d337fb2ef367773da87f523094c4eea00f360c50c14a420e8ffcf', 'merkle_root': 'eed45dd756517e1e8dac73d178af8b6fb8664b9b0f2385abe488f5c5c85dcc80', 'timestamp': 1648460399, 'bits': 436507520, 'nonce': 269863509, 'block_height': 2618838}, 2618839: {'version': 536870912, 'prev_block_hash': '31593e0e45baabf70da02418cb697776b956b0f6140fc92106d17e30232b76a7', 'merkle_root': '760533299429714c60ce6fb69c5f9412bbdaf200ada61a70f7d89e214c9dd27d', 'timestamp': 1648460422, 'bits': 436503319, 'nonce': 1775682715, 'block_height': 2618839}, 2618840: {'version': 536870912, 'prev_block_hash': '2d3ecac802f00387e683bd85ed7e26f39c5c7d47ff48f08b88e06c6777ac7fe7', 'merkle_root': '392f0d667f370dd82ed187edeef6fd22cf28cf6d3ebc2b46ab275c235c76d6f6', 'timestamp': 1648460437, 'bits': 436498822, 'nonce': 3378604955, 'block_height': 2618840}, 2618841: {'version': 536870912, 'prev_block_hash': '900ad238077d2202e62ccb6aa4a59f8fb51d4d946705f3b44bffc518b08c2d57', 'merkle_root': 'a790b08631bf5a4197c60c777d2494aa04e2c55379b5a94bdca96eb4a7b868a4', 'timestamp': 1648460591, 'bits': 436498938, 'nonce': 4141510034, 'block_height': 2618841}, 2618842: {'version': 536870912, 'prev_block_hash': '812805c998bb7c8e84f1b79400c93615c28e2359c54360336f9c3e07b1b7ffd4', 'merkle_root': 'fddc9ad8f6d015b4042d1fc32b4640a38f0a283ca09c52a4acc5962d66e5a5d8', 'timestamp': 1648460758, 'bits': 436498246, 'nonce': 415940208, 'block_height': 2618842}, 2618843: {'version': 536870912, 'prev_block_hash': 'b2b8f1e6ded99d84e99e0194955ce538f147d062d5060e130e983a9995fb5770', 'merkle_root': '319699580679fef7c4a7c22fe6c64189db7605f3cb910487e58cf43e0173100f', 'timestamp': 1648460769, 'bits': 436521324, 'nonce': 3036675217, 'block_height': 2618843}, 2618844: {'version': 536870912, 'prev_block_hash': '13231a5a5e458edf4027cc98761d5911f6552fcec4d3c584dae6231c7b9ff3d4', 'merkle_root': '4d82845d4e521e83b29b51e1a277bdc01cbfa9bd60a46bc802d29bcb3e3969f7', 'timestamp': 1648460803, 'bits': 436514059, 'nonce': 1004669485, 'block_height': 2618844}, 2618845: {'version': 536870912, 'prev_block_hash': 'f105722bb3eaa7c3a72bbe0b3a0d2e4dca7c3eb0ac99024cb3184a1ef4b61849', 'merkle_root': '2312a58d37c5b64cb80f912246921dffb3b7cbbe103c15e235234399a68cf97f', 'timestamp': 1648460960, 'bits': 436514216, 'nonce': 436115352, 'block_height': 2618845}, 2618846: {'version': 536870912, 'prev_block_hash': 'd9e13fea4178d7c1297a829286f852fc5943eff591c7605c3b7d9159ae48fd56', 'merkle_root': 'c8231cb745855325b6f289b70f244b314bfa4576778ce68d4248f192fb5b9b00', 'timestamp': 1648461089, 'bits': 436533225, 'nonce': 738857817, 'block_height': 2618846}, 2618847: {'version': 536870912, 'prev_block_hash': 'ce5e4cdc7ade069ea9acc89da7238e0383c843b6ca3f9f568cfae6604bd82008', 'merkle_root': 'fbd66c4191fec47ec659c077fd3f91d6bb97cd609743d2696b6d0f674daffc01', 'timestamp': 1648461211, 'bits': 436545784, 'nonce': 404729918, 'block_height': 2618847}, 2618848: {'version': 536870912, 'prev_block_hash': '20de40cbf2e95e25384958acdb24e42f58b54162236a9373edc8f9f88b88f1c1', 'merkle_root': '5a74c24dd9611de8b5b3743d8c861ac87929a95b48fe869e40977a2feb8e9a33', 'timestamp': 1648461245, 'bits': 436533061, 'nonce': 1823956382, 'block_height': 2618848}, 2618849: {'version': 536870912, 'prev_block_hash': '5cf0dbc0f53f2c32f2aa0eba986246be5c5613e7ffae682af183090acd01906c', 'merkle_root': '114f67fd1ff6cd889a22b625d83b56ba7e0da172155222c62e38cd9cf1a84f94', 'timestamp': 1648461382, 'bits': 436522902, 'nonce': 1987662146, 'block_height': 2618849}, 2618850: {'version': 536870912, 'prev_block_hash': '1ef6c82854f3f0298652f051a44fa1b4182538c9046d76225e19cebe30c3091b', 'merkle_root': 'b44c717ca554ed68775cffb7e8f33c78a3c022342c3d24a319159bd5c3568d9d', 'timestamp': 1648461436, 'bits': 436533004, 'nonce': 510278843, 'block_height': 2618850}, 2618851: {'version': 536870912, 'prev_block_hash': '007dd09b5f3b3c3c624f14a4152f87104caeaff1c2897dd314e88723dfcacc40', 'merkle_root': 'c210f401f9d64902303e390dc73dd344083d2e711b1879119266b38788057cfb', 'timestamp': 1648461555, 'bits': 436540340, 'nonce': 1439585998, 'block_height': 2618851}, 2618852: {'version': 536870912, 'prev_block_hash': '1df92449c32a66ed1b392caa4e1b2da97c4b6e3ec4d83f0f8319a408c4a2fb07', 'merkle_root': '8fa879f3c8c0391e4d07f8eef0740013b9f558733eca510d0286f5f171f523db', 'timestamp': 1648461574, 'bits': 436503999, 'nonce': 589639930, 'block_height': 2618852}, 2618853: {'version': 536870912, 'prev_block_hash': '74257004c0cc6bbecfc5a25e3800317804dbfc110f03dbe47dd290cc170f0a61', 'merkle_root': '8f2699243eebe437c056ab9fe506f5502079f8d07c0ae5cba856f5979ad162ee', 'timestamp': 1648461846, 'bits': 436506247, 'nonce': 2438300719, 'block_height': 2618853}, 2618854: {'version': 536870912, 'prev_block_hash': '4c3e88e94ea219b64e20e90967b34e5b80b67c00705dd8e10b197988052cdbc7', 'merkle_root': '921a967bf362ec043e05b4f476d4f8da04daaef567046ec794e7b0ece3da40bd', 'timestamp': 1648462034, 'bits': 436534798, 'nonce': 3649343042, 'block_height': 2618854}, 2618855: {'version': 536870912, 'prev_block_hash': '7d579c2330057b1dc8ac47a7fcecb8cdc463221dfbde83a7e217d14168f106c8', 'merkle_root': 'bfc376f5f7dd7a99e389c31246a518f8dcb380c0e2815d813fdd366c616eea48', 'timestamp': 1648462104, 'bits': 436565033, 'nonce': 2563509740, 'block_height': 2618855}, 2618856: {'version': 536870912, 'prev_block_hash': 'b8e6ba10d974101d6f78d04140a7cf82ad58193f9a3f83efb1010ca258a7d76b', 'merkle_root': '6dc70ec7613b18bcc6743fe4bf3cf78d34f866d3cfe7fa7a48968248c5ef5572', 'timestamp': 1648462121, 'bits': 436562680, 'nonce': 143393921, 'block_height': 2618856}, 2618857: {'version': 536870912, 'prev_block_hash': '4a46079a228a9e3fc8f026225554c5fad0748ff043996bc29668a6acb006df36', 'merkle_root': '312487b8fe7118b8d34914576cc8a6c602bc201c080eeffb55eb8db6705a4a5a', 'timestamp': 1648462183, 'bits': 436567829, 'nonce': 92461383, 'block_height': 2618857}, 2618858: {'version': 536870912, 'prev_block_hash': '0993c3db605515a076e89bed703591cd4d239fd4c9ecb98bcc79128d0abf7636', 'merkle_root': '17e8bb232a6cbdea0158dda9b0c6ad89e2e2a8f59e6db0b1853a3f567250a1be', 'timestamp': 1648462213, 'bits': 436566189, 'nonce': 2031109918, 'block_height': 2618858}, 2618859: {'version': 536870912, 'prev_block_hash': 'c1e63aec511f157c0804a3564b83b7358a2a01b1d47833f25d371168a0ac5844', 'merkle_root': '9c31b9a1d89e29751a058eb11ca3f51621daa03b5c0b03e02582879ae7b3d7c7', 'timestamp': 1648462421, 'bits': 436518746, 'nonce': 861655327, 'block_height': 2618859}, 2618860: {'version': 536870912, 'prev_block_hash': '1b1508e1a9846c0bd0ffca090fd6a598653b268f46e19e9bcf36f04ae76a4d72', 'merkle_root': '7b313b0e05325df57a4d989e08adb5bd68005d7771d63ceba87d7be5de431f52', 'timestamp': 1648462583, 'bits': 436519201, 'nonce': 925380454, 'block_height': 2618860}, 2618861: {'version': 536870912, 'prev_block_hash': '7a23e0127126539c21c1f3c144f10419e1795c940e4abc956e4ea3b7b0b3fe55', 'merkle_root': 'aefc57b5d0266fea4b85960f0f27dc7d6249c194336b2dcb8c62be1784325f68', 'timestamp': 1648462589, 'bits': 436529747, 'nonce': 1864455459, 'block_height': 2618861}, 2618862: {'version': 536870912, 'prev_block_hash': 'e0126b92d0a62fc8ad328b31400de07abcf4594ed7e7280dfac4a39baa132fe4', 'merkle_root': 'e20acc91f6310989a6d0563f52aa46a98b672e94f5418c74261b8e7c8b2ebf89', 'timestamp': 1648462630, 'bits': 436531191, 'nonce': 1047130036, 'block_height': 2618862}, 2618863: {'version': 536870912, 'prev_block_hash': '1401e5fbbbe63d40e6b70697ecf9503777a2d050c69a96265900f35837a16ade', 'merkle_root': '6b60d51b4c6862c5cd1453972e79b22cc038cfb58540ae0fd5181c083b09a9f3', 'timestamp': 1648462645, 'bits': 436534878, 'nonce': 1487570091, 'block_height': 2618863}, 2618864: {'version': 536870912, 'prev_block_hash': '7a7215c3957fa3d9fe3b37a837bce3fa828db722370577c0328a5108ce3da9d5', 'merkle_root': 'df9dfb9be35337566cf6c3db3cc685abd79a8e10ac9ef305288f016f40f6b21a', 'timestamp': 1648462660, 'bits': 436536319, 'nonce': 2976770660, 'block_height': 2618864}, 2618865: {'version': 536870912, 'prev_block_hash': '600b7e876629645b57a7402c08d9d57b33fd2374dc35b72577a30183e4377bc4', 'merkle_root': 'd2f1b2b16bdc167312046dd833d8886cffb65d74fa1e1f3a9b415fb37544e7f3', 'timestamp': 1648462752, 'bits': 436517118, 'nonce': 17477312, 'block_height': 2618865}, 2618866: {'version': 536870912, 'prev_block_hash': '72554589ecf30ac266e04beba9dce46fc8f4876001f7a912a216eb6a0295e3a9', 'merkle_root': 'c772113336de074c86c1f3c184562e2b5dc9b827cfa917e2efde6ddfd9d5300f', 'timestamp': 1648462877, 'bits': 436505861, 'nonce': 2781207808, 'block_height': 2618866}, 2618867: {'version': 536870912, 'prev_block_hash': 'c1493789e5005f0af00d0b7124f42ca4282b13392b377ae4f8471c709ded59e7', 'merkle_root': '269952518d02910f8f207124caac20039b6b06e246c71a2bbf72992dd8155da4', 'timestamp': 1648462906, 'bits': 436522770, 'nonce': 2233212507, 'block_height': 2618867}, 2618868: {'version': 536870912, 'prev_block_hash': '2331ab96b79a11e7eebded290530c88203fe0d822553fe52d9cbd177dab4ce44', 'merkle_root': 'd3208e7b1b5d73e6fbb5e82db71de57a08c9b71162517099161b82da4fa79f5e', 'timestamp': 1648462970, 'bits': 436522737, 'nonce': 1065251414, 'block_height': 2618868}, 2618869: {'version': 536870912, 'prev_block_hash': '1bb6b3477285a8f3db0a43f3cf3e877f1ca7556fdee4ef52a753c8bd9bc2cfd7', 'merkle_root': '9f6a57bf55ca04c223991210026b191305266a860e03ed53424b50b8ed950768', 'timestamp': 1648463002, 'bits': 436509123, 'nonce': 809487759, 'block_height': 2618869}, 2618870: {'version': 536870912, 'prev_block_hash': 'f148a2d8d6383fe90d77c8ead006213ede4aab028507e9aa006095d8c670f729', 'merkle_root': 'a538ad39f95950836d68ac3b1a303329c2f9cbd065770cf591dc8f7b6dacb968', 'timestamp': 1648463181, 'bits': 436493910, 'nonce': 3298181730, 'block_height': 2618870}, 2618871: {'version': 536870912, 'prev_block_hash': '7f222ff89da327813e387d2e7a819f2ed5be41462fa34ec3043e02303b42f395', 'merkle_root': 'd53f2b5ca71cdc390dd58477305105e5224d6eaad90a64271dfd23f79252c5ee', 'timestamp': 1648463279, 'bits': 436500452, 'nonce': 2164918962, 'block_height': 2618871}, 2618872: {'version': 536870912, 'prev_block_hash': '61b0bbcd79ef4464e8a80e1d49794d03b488171b9b716f4f1c7562f9d86c4d89', 'merkle_root': 'feb518bf55f7195ac6e9a1f3004eac35be3b9ad3f02b47aa15c01e737481f06f', 'timestamp': 1648463350, 'bits': 436508504, 'nonce': 487224662, 'block_height': 2618872}, 2618873: {'version': 536870912, 'prev_block_hash': '066d18ed2c7a880eedcd439e0299cbc99d25405b1f27d0771d64ed52c9fc3e3a', 'merkle_root': 'f0f1094dda51968faccdfba9faf0b330a54c3c07bac188691f9d29b22546c88b', 'timestamp': 1648463498, 'bits': 436498139, 'nonce': 1075684871, 'block_height': 2618873}, 2618874: {'version': 536870912, 'prev_block_hash': '6daa3c20342ef2586ecb91f67ae09130f38992accdd92e0c0e6a86110d7b8693', 'merkle_root': '3b247a30e8ba18b12b498413baf96092b717b83b8d3a2637ac08c644d394c2d2', 'timestamp': 1648463531, 'bits': 436510674, 'nonce': 2571078931, 'block_height': 2618874}, 2618875: {'version': 536870912, 'prev_block_hash': '90fb5e4e4a6ba1449ac9b2e958396ba836c3305ac95135e5e5ea425cf897f07e', 'merkle_root': '52601997f0036fabd069f87ff94d860d4118f4027f42b291936ef502aeb11ac3', 'timestamp': 1648463754, 'bits': 436497676, 'nonce': 2344600200, 'block_height': 2618875}}
        bits = Blockchain.get_target(self, 2618875, headers5)
        self.assertEqual(bits, 7112266753876343510151023106557578774485394364773876493401627)
