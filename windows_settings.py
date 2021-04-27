import os, pickle


class WindowInfo:
    ordering = ['hp', 'mp', 'party_dead', 'hp_party', 'mp_party', 'buff', 'target_hp']

    def __init__(self):
        self.values = [{'active': 0, 'name': '',
                        'triggers': {'hp': [], 'mp': [], 'party_dead': [], 'hp_party': [], 'mp_party': [], 'buff': [],
                                     'target_hp': []}}
                       for x in range(9)]
        self.load()

    def save(self):
        if not os.path.exists('save'):
            os.makedirs('save')
        with open('save/window_bind.l2b', 'wb') as f:
            pickle.dump(self.values, f)

    def load(self):
        if os.path.exists('save/window_bind.l2b'):
            with open('save/window_bind.l2b', 'rb') as f:
                try:
                    self.values = pickle.load(f)
                except:
                    pass

    def delete_by_i(self, window_i, del_i):
        window_tr = self[window_i]['triggers']

        i = 0
        while del_i > len(self.sum_tr_list(window_i, i)) - 1:
            i += 1
        i -= 1
        if i == 0:
            window_tr[self.ordering[i]].pop(del_i)
        elif i > 0:
            window_tr[self.ordering[i]].pop(del_i - len(self.sum_tr_list(window_i, i)))

    def sum_tr_list(self, window_i, count):
        window_tr = self[window_i]['triggers']
        l = []
        for i in range(min(count, len(self.ordering))):
            l += window_tr[self.ordering[i]]
        return l

    def __getitem__(self, item):
        return self.values[item]

    def __str__(self):
        return str(self.values)
