# _*_ coding: utf-8 _*_


class TrieNode:
    def __init__(self):
        self.index = 0
        self.layer = 0
        self.end = False
        self.char = ''
        self.results = []
        self.m_values = {}
        self.failure = None
        self.parent = None

    def add(self, c):
        if c in self.m_values:
            return self.m_values[c]
        node = TrieNode()
        node.parent = self
        node.char = c
        self.m_values[c] = node
        return node

    def set_results(self, index):
        if not self.end:
            self.end = True
        self.results.append(index)

    def __str__(self):
        return "char:{}; code:{}; index:{}; layer:{}; m_values:{};parent:{}:".format(chr(self.char) if self.char else 'root', self.char, self.index, self.layer, str(self.m_values), self.parent.char if self.parent else "" )


class TrieNode2:
    def __init__(self):
        self.end = False
        self.results = []
        self.m_values = {}
        self.min_flag = 0xffff
        self.max_flag = 0

    def add(self, c, node3):
        if self.min_flag > c:
            self.min_flag = c
        if self.max_flag < c:
            self.max_flag = c
        self.m_values[c] = node3

    def set_results(self, index):
        if not self.end:
            self.end = True
        if index not in self.results:
            self.results.append(index)

    def has_key(self, c):
        return c in self.m_values

    def try_get_value(self, c):
        if self.min_flag <= c <= self.max_flag:
            if c in self.m_values:
                return self.m_values[c]
        return None

class WordsSearch:

    skip_word_filter = None

    _skip_list = " \t\r\n~!@#$%^&*()_+-=【】、[]{}|;':\"，。、《》？αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀｜〃〔〕〈〉《》「」『』．〖〗【】（）［］｛｝ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩①②③④⑤⑥⑦⑧⑨⑩⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇≈≡≠＝≤≥＜＞≮≯∷±＋－×÷／∫∮∝∞∧∨∑∏∪∩∈∵∴⊥∥∠⌒⊙≌∽√§№☆★○●◎◇◆□℃‰€■△▲※→←↑↓〓¤°＃＆＠＼︿＿￣―♂♀┌┍┎┐┑┒┓─┄┈├┝┞┟┠┡┢┣│┆┊┬┭┮┯┰┱┲┳┼┽┾┿╀╁╂╃└┕┖┗┘┙┚┛━┅┉┤┥┦┧┨┩┪┫┃┇┋┴┵┶┷┸┹┺┻╋╊╉╈╇╆╅╄"

    def __init__(self):
        self._indexs = []
        self._keywords = []
        self._skip_bit_array = {}
        for item in self._skip_list:
            self._skip_bit_array[item] = True



    def set_keywords(self, keywords):
        self._keywords = keywords
        for i in range(len(keywords)):
            self._indexs.append(i)

        root = TrieNode()
        all_node_layer = {}
        for i in range(len(self._keywords)):
            p = self._keywords[i]
            nd = root
            for j in range(len(p)):
                nd = nd.add(ord(p[j]))
                if nd.layer == 0:
                    nd.layer = j + 1
                    if nd.layer in all_node_layer:
                        all_node_layer[nd.layer].append(nd)
                    else:
                        all_node_layer[nd.layer] = []
                        all_node_layer[nd.layer].append(nd)
            nd.set_results(i)

        all_node = [root]
        for key in all_node_layer.keys():
            for nd in all_node_layer[key]:
                all_node.append(nd)

        all_node_layer = None

        for i in range(len(all_node)):
            if i == 0:
                continue
            nd = all_node[i]
            nd.index = i
            r = nd.parent.failure
            c = nd.char
            while r and c not in r.m_values:
                r = r.failure
            if not r:
                nd.failure = root
            else:
                nd.failure = r.m_values[c]
                for key2 in nd.failure.results:
                    nd.set_results(key2)

        root.failure = root

        all_node2 = []
        for i in range(len(all_node)):
            all_node2.append(TrieNode2())

        for i in range(len(all_node2)):
            old_node = all_node[i]
            new_node = all_node2[i]

            for key in old_node.m_values:
                index = old_node.m_values[key].index
                new_node.add(key, all_node2[index])

            for index in range(len(old_node.results)):
                item = old_node.results[index]
                new_node.set_results(item)

            old_node = old_node.failure
            while old_node != root:
                for key in old_node.m_values:
                    if not new_node.has_key(key):
                        index = old_node.m_values[key].index
                        new_node.add(key, all_node2[index])
                for index in range(len(old_node.results)):
                    item = old_node.results[index]
                    new_node.set_results(item)
                old_node = old_node.failure
        all_node = None
        root = None
        self._first = all_node2[0]

    def contains_any(self, text):
        ptr = None
        for index in range(len(text)):
            if text[index] in self._skip_list:
                continue
            t = ord(text[index])
            tn = None
            if not ptr:
                tn = self._first.try_get_value(t)
            else:
                tn = ptr.try_get_value(t)
                if not tn:
                    tn = self._first.try_get_value(t)

            if tn:
                if tn.end:
                    return True
            ptr = tn
        return False

    def find_all(self, text):
        ptr = None
        list = []
        for index in range(len(text)):
            if text[index] in self._skip_list:
                continue
            t = ord(text[index])
            tn = None
            if not ptr:
                tn = self._first.try_get_value(t)
            else:
                tn = ptr.try_get_value(t)
                if not tn:
                    tn = self._first.try_get_value(t)
            if tn:
                if tn.end:
                    for j in range(len(tn.results)):
                        item = tn.results[j]
                        keyword = self._keywords[item]
                        list.append(
                            {"Keyword": keyword, "Success": True, "End": index, "Start": index + 1 - len(keyword),
                             "Index": self._indexs[item]})
            ptr = tn
        return list

    def find_first(self, text):
        ptr = None
        for index in range(len(text)):
            if text[index] in self._skip_list:
                continue
            t = ord(text[index])
            tn = None
            if (ptr == None):
                tn = self._first.try_get_value(t)
            else:
                tn = ptr.TryGetValue(t)
                if (tn == None):
                    tn = self._first.try_get_value(t)

            if tn:
                if tn.end:
                    item = tn.results[0]
                    keyword = self._keywords[item]

                    return {"Keyword": keyword, "Success": True, "End": index, "Start": index + 1 - len(keyword),
                            "Index": self._indexs[item]}
            ptr = tn
        return None

    def replace(self, text, replace_char='*'):
        result = list(text)

        ptr = None
        for i in range(len(text)):
            if text[i] in self._skip_list:
                continue
            t = ord(text[i])
            tn = None
            if not ptr:
                tn = self._first.try_get_value(t)
            else:
                tn = ptr.TryGetValue(t)
                if not tn:
                    tn = self._first.try_get_value(t)

            if tn:
                if tn.end:
                    maxLength = len(self._keywords[tn.Results[0]])
                    start = i + 1 - maxLength
                    for j in range(start, i + 1):
                        result[j] = replace_char
            ptr = tn
        return ''.join(result)


if __name__ == "__main__":

    import time
    s = "巧克力|力量"
    test = "巧αβγδεζηθ \t克力"
    t = time.process_time()
    search = WordsSearch()
    search.set_keywords(s.split('|'))

    b = search.contains_any(test)
    print(b, ':result')
    print('Cost is %6.6f' % (time.process_time() - t))

    import paddlehub as hub
    porn_detection_lstm = hub.Module(name="porn_detection_lstm")
    import paddlenlp as ppnlp
    ppnlp.transformers
