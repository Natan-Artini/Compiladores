import os
from af.inputfile import Constructor
from ts.__main__ import SymbolTable


def main():
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    file_path = os.path.join(dir_path, 'tokens_GRs.txt')
    csv_path = os.path.join(dir_path, 'AFD_output.csv')

    # AUTÔMATO FINITO
    # TODO: O Autômato está considerando o '.' como estado de erro quando tem números na frente.
    af = Constructor(file_path)
    af.fill_afnd()  # preenche o AFND com os dados do arquivo de entrada
    # af.print_afnd()  # imprime o AFND carregado
    af.remove_epsilon()  # remove os EPSILON transições
    # af.print_afnd()  # imprime o AFND livre de épsilon transições
    af.afnd_determinization()  # determiniza o afnd
    # af.print_afd()  # imprime o AFD
    af.remove_dead()  # remove os estados mortos
    af.remove_unreachable()  # remove os estados inatingíveis
    af.print_afd()  # imprime o AFD finalizado
    # af.export_csv(csv_path)

    #  TABELA DE SÍMBOLOS
    ts = SymbolTable()  # Instância da Tabela de Símbolos
    ts.build_symbol_table(af)  # Constrói a Tabela de Símbolos de acordo com o AF
    ts.show_symbol_table()  # Mostra Tabela de Símbolos

'''
    print('\n\nAlfabeto da linguagem: {}\n\n'.format(af.alphabet))

    contin = 'S'

    while contin == 'S':
        token = str(input('Digite o token a ser verificado: '))
        recognized, state, message = af.token_recognition(token)
        print('Reconhecido = {} | ID = {} | {}'.format(recognized, state, message))
        contin = str(input('Deseja continuar? S/N: ')).upper()

    print('Saindo...')
'''

main()
