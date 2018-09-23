from iota import Iota, Bundle


class Replay:
    """
    Class for managing reattachments.
    """

    def __init__(self, node, seed, bundle, replay_callback=None, depth=7, min_weight_magnitude=14):
        """
        API dict to talk to IRI node
        """

        self.api = Iota(node, seed)

        """
        Depth used for reattachment.
        """

        self.depth = depth

        """
        Min weight magnitude used by reattachments.
        """

        self.min_weight_magnitude = min_weight_magnitude

        if replay_callback:
            """
            Alert callback to trigger when reattachment is done.
            """
            self.replay_callback = replay_callback

        self.replay(bundle)

    def fetch_tail_transaction(self, bundle_hash):
        """
        Finds tail transaction hash.

        :param bundle_hash:
          str: Bundle hash.

        :return:
          str: Tail transaction hash.
        """

        ft_result = self.api.find_transactions(bundles=[bundle_hash])
        transaction_hashes = ft_result['hashes']

        gt_result = self.api.get_trytes(transaction_hashes)
        bundle = Bundle.from_tryte_strings(gt_result['trytes'])

        return bundle.tail_transaction.hash

    def replay(self, bundle):
        """
        Reattaches bundle.

        :param bundle:
          str: Bundle hash.

        :return:
          None
        """

        tail_transaction = self.fetch_tail_transaction(bundle)

        try:
            self.api.replay_bundle(
                transaction=tail_transaction,
                depth=self.depth,
                min_weight_magnitude=self.min_weight_magnitude
            )
            if callable(self.replay_callback):
                self.replay_callback('Successfully replayed your specified bundle!')
        except:
            if callable(self.replay_callback):
                self.replay_callback('Something went wrong while replaying your bundle! Please try again.')


