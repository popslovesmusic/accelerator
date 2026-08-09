import unittest

class TestAlternativeTriadSemantics(unittest.TestCase):
    def test_semantic_comparison(self):
        # We define rival closure semantic families:
        # 1. Standard cycle closure (3-Peak Rule): forbidden if active_count == 2
        # 2. Exactly-one-active closure: allowed if active_count == 1
        # 3. Directed cycle: active_count == 3 only
        # 4. Parity: allowed if active_count % 2 == 1
        
        assignments = [
            {"active_count": 0, "allowed_standard": True, "allowed_exactly_one": False, "allowed_parity": False},
            {"active_count": 1, "allowed_standard": True, "allowed_exactly_one": True, "allowed_parity": True},
            {"active_count": 2, "allowed_standard": False, "allowed_exactly_one": False, "allowed_parity": False},
            {"active_count": 3, "allowed_standard": True, "allowed_exactly_one": False, "allowed_parity": True}
        ]
        
        # Verify distinction between standard and alternative models
        for item in assignments:
            # Under standard cycle closure (3-Peak), active counts of 0, 1, 3 are allowed
            allowed_std = not (item["active_count"] == 2)
            self.assertEqual(allowed_std, item["allowed_standard"])
            
            # Under exactly-one-active, only active count of 1 is allowed
            allowed_exact = (item["active_count"] == 1)
            self.assertEqual(allowed_exact, item["allowed_exactly_one"])
            
            # Under parity, active counts of 1, 3 are allowed
            allowed_par = (item["active_count"] % 2 == 1)
            self.assertEqual(allowed_par, item["allowed_parity"])

if __name__ == "__main__":
    unittest.main()
