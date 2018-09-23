from iota import Iota, Bundle, TransactionHash


class Promote:
    """
    Class for managing promotions.
    """

    def __init__(self, node, bundle, alert_callback=None, depth=7, min_weight_magnitude=14):
        """
        API dict to talk to IRI node
        """

        self.api = Iota(node)

        """
        Depth used for promotion.
        """

        self.depth = depth

        """
        Min weight magnitude used by promotion
        """

        self.min_weight_magnitude = min_weight_magnitude

        if alert_callback:
            """
            Alert callback to trigger when promotion is done.
            """
            self.alert_callback = alert_callback

        self.promote(bundle)

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

    def promote(self, bundle):
        """
        Promotes transaction.

        :param bundle:
          str: Bundle hash.

        :return:
          None
        """

        tail_transaction = self.fetch_tail_transaction(bundle)

        try:
            inclusion_states = self.api.get_latest_inclusion(hashes=[tail_transaction])

            if inclusion_states['states'][TransactionHash(tail_transaction)] is True:
                if callable(self.alert_callback):
                    self.alert_callback('Transaction already confirmed')
            else:
                self.api.promote_transaction(
                    transaction=tail_transaction,
                    depth=self.depth,
                    min_weight_magnitude=self.min_weight_magnitude
                )

                if callable(self.alert_callback):
                    self.alert_callback('Successfully promoted your specified transaction!')
        except Exception:
            if callable(self.alert_callback):
                self.alert_callback('Something went wrong while promoting your bundle! Please try again.')


