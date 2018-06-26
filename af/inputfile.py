import copy
# from collections import OrderedDict

EPSILON = ''


def is_sublist(sublist, list):
    return set(sublist) <= set(list)


class AFNDLine(dict):
    def __init__(self, initial=False, final=False, error=False, *args, **kwargs):
        super(AFNDLine, self).__init__(*args, **kwargs)
        self.initial = initial
        self.final = final
        self.error = error


class Constructor(object):

    def __init__(self, filename):
        self.afnd = dict()
        self.afd = dict()
        self.file = open(filename, 'r')
        self.tokens = []
        self.alphabet = []  # alfabeto da linguagem
        self.initial_state = 0  # estado inicial
        self.state = 0  # estado incremento
        self.error_state = None  # estado de erro
        self.keep = []  # lista de estados atingíveis e vivos
        self.related_states = {}  # dicionário para relacionar indeterminismos à novos estados
        self.afnd_line(self.initial_state, initial=True)  # cria o estado inicial

    def print_afnd(self):
        print('Tokens encontrados: {}'.format(self.tokens))
        print('Alfabeto da linguagem: {}'.format(self.alphabet))
        print('AFND:')
        for key, value in self.afnd.items():
            i = ''
            f = ''
            e = ''
            if value.initial:
                i = '->'
            if value.final:
                f = '*'
            if value.error:
                e = '(E)'
            print('{}{}{}{}: {}'.format(i, f, e, key, value))

    def print_afd(self):
        print('AFD:')
        for key, value in self.afd.items():
            i = ''
            f = ''
            e = ''
            if value.initial:
                i = '->'
            if value.final:
                f = '*'
            if value.error:
                e = '(E)'
            print('{}{}{}{}: {}'.format(i, f, e, key, value))

    def update_alphabet(self, symbols=None):
        """
        Atualiza o alfabeto da linguagem
        :param symbols: list: lista de símbolos que serão adicionados ao alfabeto
        """
        if symbols and not is_sublist(symbols, self.alphabet):
            self.alphabet = list(set(self.alphabet+symbols))

    def afnd_line(self, state, initial=False, final=False, alphabet=None):
        """
        Cria uma nova linha no AFND com o estado e preenche as colunas com listas vazias em cada posição
        correspondente do alfabeto
        :param state: int: estado a ser criado
        :param initial: bool: se o estado informado é inicial
        :param final: bool: se o estado informado é final
        :param alphabet: list: lista de chars
        """
        if alphabet:
            self.update_alphabet(alphabet)  # atualiza o alfabeto

        if state not in self.afnd:  # se o estado não existe cria-se uma nova linha
            self.afnd[state] = AFNDLine(initial=initial, final=final)

        # atualiza se o estado é inicial e/ou final
        if initial:
            self.afnd[state].initial = initial
        if final:
            self.afnd[state].final = final

        for sym in self.alphabet:  # cria uma coluna para cada símbolo do alfabeto informado que ainda não existe
            if sym not in self.afnd[state]:
                self.afnd[state][sym] = []

    def afd_line(self, state, initial=False, final=False, alphabet=None):
        """
        Cria uma nova linha no AFD com o estado e preenche as colunas com listas vazias em cada posição
        correspondente do alfabeto
        :param state: int: estado a ser criado
        :param initial: bool: se o estado informado é inicial
        :param final: bool: se o estado informado é final
        :param alphabet: list: lista de chars
        """
        if alphabet:
            self.update_alphabet(alphabet)  # atualiza o alfabeto

        if state not in self.afd:  # se o estado não existe cria-se uma nova linha
            self.afd[state] = AFNDLine(initial=initial, final=final)

        # atualiza se o estado é inicial e/ou final
        if initial:
            self.afd[state].initial = initial
        if final:
            self.afd[state].final = final

        for sym in self.alphabet:  # cria uma coluna para cada símbolo do alfabeto informado que ainda não existe
            if sym not in self.afd[state]:
                self.afd[state][sym] = []

    def clean_afd(self):
        """
        Limpa o AFD e adiciona o estado de erro nos não mapeados
        """
        if not self.error_state:
            self.afd_line(self.state+1)
            self.afd[self.state+1].error = True
            self.error_state = self.state+1
            self.state += 1

        for state in list(self.afd):
            for sym in self.alphabet:  # cria uma coluna para cada símbolo do alfabeto informado que ainda não existe
                if (sym not in self.afd[state]) or (self.afd[state][sym] == []):
                    self.afd[state][sym] = self.error_state
                else:
                    self.afd[state][sym] = self.afd[state][sym][0]

    def update_afnd(self):
        """
        Preenche as lacunas vazias do AFND
        """
        for state in list(self.afnd):
            self.afnd_line(state)

    def add_afnd_step(self, origin_state, dest_state, symbol, origin_initial, origin_final, dest_initial, dest_final):
        """
        Adiciona um passo no autômato
        :param origin_state: int: estado de origem
        :param dest_state: int: estado de destino
        :param symbol: str: símbolo reconhecido
        :param origin_initial: bool: estado de origem é inicial?
        :param origin_final: bool: estado de origem é final?
        :param dest_initial: bool: estado de destino é inicial?
        :param dest_final: bool: estado de destino é final?
        """
        self.afnd_line(origin_state, origin_initial, origin_final, [symbol])
        self.afnd_line(dest_state, dest_initial, dest_final)

        self.afnd[origin_state][symbol].append(dest_state)
        self.afnd[origin_state][symbol] = list(set(self.afnd[origin_state][symbol]))

    def add_afd_step(self, origin_state, dest_state, symbol, origin_initial, origin_final, dest_initial, dest_final):
        """
        Adiciona um passo no autômato determinístico
        :param origin_state: int: estado de origem
        :param dest_state: int: estado de destino
        :param symbol: str: símbolo reconhecido
        :param origin_initial: bool: estado de origem é inicial?
        :param origin_final: bool: estado de origem é final?
        :param dest_initial: bool: estado de destino é inicial?
        :param dest_final: bool: estado de destino é final?
        """
        self.afd_line(origin_state, origin_initial, origin_final, [symbol])
        self.afd_line(dest_state, dest_initial, dest_final)

        self.afd[origin_state][symbol].append(dest_state)
        self.afd[origin_state][symbol] = list(set(self.afd[origin_state][symbol]))

    def productions_to_dict(self, productions=''):
        """
        Transforma o lado direito das gramáticas em dados estruturados para que possamos trabalhar
        :param productions: str: o que vem depois de ::= na linha
        :return: dict: dicionário de valores com o padrão {produção: ESTADO}
        """
        new_data = {}
        final = False  # verifica se o estado é final (se há épsilon produção)
        productions = productions.split('|')

        for prod in productions:
            prod = prod.strip()  # elimina eventuais espaços extras entre | e a produção

            if prod:
                if prod == '&':  # épsilon produção
                    final = True
                    continue
                elif prod.startswith('<'):  # épsilon transição
                    state = prod.replace('<', '').replace('>', '')
                    symbol = EPSILON
                else:  # GR linear à direita (padrão adotado)
                    symbols = prod.split('<')
                    symbol = symbols[0]

                    try:
                        state = symbols[1].replace('>', '')
                    except IndexError:  # há somente um símbolo terminal, deve ir para um estado de erro padrão
                        state = '#'

                new_data[symbol] = state

        return new_data, final

    def _get_keep(self, current_state, stop):
        """
        Função recursiva que obtém os estados que devemos manter
        :param current_state: int: estado atual
        :param stop: bool: flag para parar a recursão, é passado se o estado atual é um estado de erro, então pára
        """
        if current_state not in self.keep:
            self.keep.append(current_state)
        if stop is False:
            values = list(set(self.afd[current_state].values()))
            if current_state in values:
                values.remove(current_state)
            for state in values:
                self._get_keep(state, self.afd[state].error or self.afd[state].error)

    def get_keep(self, state, stop=False):
        """
        Obtém apenas os estados atingíveis ou vivos, partindo do estado inicial e chamando recursivamente para
        cada estado atingido
        :param state: int: estado inicial
        :param stop: bool: indica o estado inicial da recursão
        :return: list: lista com os números dos estados que devemos manter
        """
        self._get_keep(state, stop)
        return self.keep

    def remove_dead_and_unreachable(self):
        """
        Remove os estados inatingíveis do AFD
        """
        keep = self.get_keep(self.initial_state)
        for state in list(self.afd):
            if state not in keep:
                del self.afd[state]

    def fill_afnd(self):
        """
        Preenche o autômato finito com os dados informados no arquivo
        """
        blocks = self.file.read().split('\n\n')  # quebra o arquivo em blocos de tokens e/ou GRs

        # identifica cada bloco se é de tokens ou uma GR
        for block in blocks:
            # tokens
            if not block.startswith('<'):
                self.tokens = block.splitlines()

                # atualiza o alfabeto com todos os caracteres contidos nos tokens
                self.update_alphabet(list("".join(self.tokens)))

                for token in self.tokens:
                    for i, symbol in enumerate(token):
                        if i == 0:  # ESTADO INICIAL TOKEN
                            self.add_afnd_step(origin_state=self.initial_state,
                                               dest_state=self.state+1,
                                               symbol=symbol,
                                               origin_initial=True,
                                               origin_final=False,
                                               dest_initial=False,
                                               dest_final=(i == len(token)-1))

                        else:  # DEMAIS ESTADOS
                            self.add_afnd_step(origin_state=self.state,
                                               dest_state=self.state+1,
                                               symbol=symbol,
                                               origin_initial=False,
                                               origin_final=False,
                                               dest_initial=False,
                                               dest_final=(i == len(token)-1))

                        self.state += 1
            # GR
            else:
                lines = block.splitlines()

                related_states = {'S': 0}  # cada estado lido da GR é relacionado a um correspondente numérico do AFND

                for i, line in enumerate(lines):
                    line_data = line.split('::=')
                    key = line_data[0].strip().replace('<', '').replace('>', '')  # elimina símbolos desnecessários

                    prod_data, final = self.productions_to_dict(line_data[1])

                    # assimila símbolos não-terminais à números de estados
                    if key not in related_states:
                        related_states[key] = self.state+1
                        self.state += 1

                    for prod, state in prod_data.items():

                        # assimila símbolos não-terminais à números de estados
                        if state not in related_states:
                            related_states[state] = self.state+1
                            self.state += 1

                        self.add_afnd_step(origin_state=related_states[key],
                                           dest_state=related_states[state],
                                           symbol=prod,
                                           origin_initial=False,
                                           origin_final=final,
                                           dest_initial=False,
                                           dest_final=True if state == '#' else False)

        self.update_afnd()  # atualiza preenchendo as colunas vazias

        self.afd = copy.deepcopy(self.afnd)  # cria uma cópia do AFND para o AFD que vamos mexer
        changed = self.afnd_determinization()  # determiniza o afnd
        while changed:
            changed = self.afnd_determinization()

        self.clean_afd()  # limpa o AFD e adiciona o estado de erro
        self.remove_dead_and_unreachable()  # remove os estados inatingíveis e mortos

    def afnd_determinization(self):
        """
        Cria uma cópia do AFND e determiniza esta cópia
        """
        changed = False

        for state in list(self.afd):
            for symbol in list(self.afd[state]):
                state_list = self.afd[state][symbol]

                if len(state_list) not in (0, 1):  # existe indeterminismo
                    changed = True

                    new_state = state_list
                    new_state.sort()
                    new_state = str(new_state)

                    dest_final = False

                    # se um dos estados for final o novo também será
                    for s in state_list:
                        if self.afd[s].final:
                            dest_final = True
                            break

                    if new_state not in self.related_states:
                        self.related_states[new_state] = self.state+1
                        self.state += 1

                    self.add_afd_step(origin_state=state,
                                      dest_state=self.related_states[new_state],
                                      symbol=symbol,
                                      origin_initial=self.afd[state].initial,
                                      origin_final=self.afd[state].final,
                                      dest_initial=False,
                                      dest_final=dest_final)

                    for s in state_list:
                        for sy in list(self.afd[s]):
                            states = self.afd[s][sy]
                            self.afd[self.related_states[new_state]][sy] = list(set(self.afd[self.related_states[new_state]][sy]+states))

                    self.afd[state][symbol] = [self.related_states[new_state]]

        return changed

    def token_recognition(self, token=''):
        """
        Faz o reconhecimento de um token utilizando o AFD
        :param token: str: token a ser reconhecido
        :return: tuple: tupla com (token reconhecido? (bool), estado onde parou (int), mensagem com dados do reconhecimento (str))
        """
        recognized = False
        state = self.initial_state

        if not token:
            message = 'Token não informado'
            return recognized, state, message

        for letter in token:
            line = self.afd[state]
            letter = letter.lower()

            if letter not in self.alphabet:
                message = 'Letra "{}" não pertence ao alfabeto da linguagem'.format(letter)
                return recognized, state, message

            state = line.get(letter)

        afd_data = self.afd[state]
        recognized = afd_data.final and not afd_data.error
        message = 'Inicial = {} | Final = {} | Erro = {}'.format(afd_data.initial, afd_data.final, afd_data.error)

        return recognized, state, message
