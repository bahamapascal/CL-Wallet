from iota import Iota, Bundle


class Replay:
    def __init__(self, node, seed, bundle, replay_callback=None, depth=7, min_weight_magnitude=14):
        self.api = Iota(node, seed)

        self.depth = depth
        self.min_weight_magnitude = min_weight_magnitude

        if replay_callback:
            self.replay_callback = replay_callback

        self.replay(bundle)

    def fetch_tail_transaction(self, bundle_hash):
        ft_result = self.api.find_transactions(bundles=[bundle_hash])
        transaction_hashes = ft_result['hashes']

        gt_result = self.api.get_trytes(transaction_hashes)
        bundle = Bundle.from_tryte_strings(gt_result['trytes'])

        return bundle.tail_transaction.hash

    def replay(self, bundle):
        tail_transaction = self.fetch_tail_transaction(bundle)
        self.api.replay_bundle(
            transaction=tail_transaction,
            depth=self.depth,
            min_weight_magnitude=self.min_weight_magnitude
        )

        if callable(self.replay_callback):
            self.replay_callback()
