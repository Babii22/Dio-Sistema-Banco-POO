from abc import ABC, abstractmethod
from datetime import date

# === TRANSAÇÕES ===

class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__ (self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            print(f"Depósito de R${self.valor:.2f} realizado com sucesso!")

class Saque(Transacao):
    def __init__ (self, valor):
        self.valor = valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            print(f"Saque de R${self.valor:.2f} realizado com sucesso!")
        else:
            print("Saque não realizado.")

# === HISTÓRICO ===

class Historico:
    def __init__ (self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)

# === CONTA E CONTA CORRENTE ===

class Conta:
    def __init__ (self, cliente, numero, agencia='0001'):
        self.saldo = 0.0
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)

    def sacar(self, valor):
        if valor <= 0 or valor > self.saldo:
            print("Saldo insuficiente ou valor inválido.")
            return False
        self.saldo -= valor
        self.historico.adicionar_transacao(Saque(valor))
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido para depósito.")
            return False
        self.saldo += valor
        self.historico.adicionar_transacao(Deposito(valor))
        return True

    def extrato(self):
        print(f"\n=== EXTRATO - Conta {self.numero} ===")
        for t in self.historico.transacoes:
            tipo = t.__class__.__name__
            valor = t.valor
            print(f"{tipo}: R${valor:.2f}")
        print(f"Saldo atual: R${self.saldo:.2f}")

class ContaCorrente(Conta):
    def __init__ (self, cliente, numero, limite=500.0, limite_saques=3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0

    def sacar(self, valor):
        if self.saques_realizados >= self.limite_saques:
            print("Limite de saques atingido.")
            return False
        if valor > (self.saldo + self.limite):
            print("Limite insuficiente.")
            return False
        if super().sacar(valor):
            self.saques_realizados += 1
            return True
        return False

# === CLIENTES ===

class Cliente:
    def __init__ (self, endereco):
        self.endereco = endereco
        self.contas = []

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

class PessoaFisica(Cliente):
    def __init__ (self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)  # Corrigido aqui: __init_ com dois underlines
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def __str__ (self):
        return f"{self.nome} - CPF: {self.cpf}"

# === FUNÇÕES ===

def menu():
    print("\n=== MENU ===")
    print("1. Criar cliente")
    print("2. Criar conta para cliente")
    print("3. Listar clientes")
    print("4. Listar contas de cliente")
    print("5. Depositar")
    print("6. Sacar")
    print("7. Extrato")
    print("0. Sair")
    return input("Escolha uma opção: ")

def selecionar_cliente(clientes):
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return None
    print("\nClientes disponíveis:")
    for i, cliente in enumerate(clientes):
        print(f"{i + 1}. {cliente}")
    try:
        indice = int(input("Escolha o número do cliente: ")) - 1
        return clientes[indice] if 0 <= indice < len(clientes) else None
    except:
        print("Opção inválida.")
        return None

def selecionar_conta(cliente):
    if not cliente.contas:
        print("Esse cliente não possui contas.")
        return None
    print(f"\nContas de {cliente.nome}:")
    for i, conta in enumerate(cliente.contas):
        print(f"{i + 1}. Conta {conta.numero} - Saldo: R${conta.saldo:.2f}")
    try:
        indice = int(input("Escolha o número da conta: ")) - 1
        return cliente.contas[indice] if 0 <= indice < len(cliente.contas) else None
    except:
        print("Opção inválida.")
        return None

# === MAIN ===

clientes = []
contador_contas = 1

while True:
    opcao = menu()

    if opcao == "1":
        nome = input("Nome: ")
        cpf = input("CPF: ")
        data = input("Data de nascimento (AAAA-MM-DD): ")
        endereco = input("Endereço: ")
        try:
            cliente = PessoaFisica(nome, cpf, date.fromisoformat(data), endereco)
            clientes.append(cliente)
            print("Cliente criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")

    elif opcao == "2":
        cliente = selecionar_cliente(clientes)
        if cliente:
            conta = ContaCorrente(cliente, numero=contador_contas)
            cliente.adicionar_conta(conta)
            print(f"Conta {contador_contas} criada com sucesso para {cliente.nome}!")
            contador_contas += 1

    elif opcao == "3":
        if clientes:
            print("\n=== CLIENTES ===")
            for cliente in clientes:
                print(cliente)
        else:
            print("Nenhum cliente cadastrado.")

    elif opcao == "4":
        cliente = selecionar_cliente(clientes)
        if cliente:
            if cliente.contas:
                print(f"\nContas de {cliente.nome}:")
                for conta in cliente.contas:
                    print(f"Conta {conta.numero} - Saldo: R${conta.saldo:.2f}")
            else:
                print("Esse cliente não possui contas.")

    elif opcao == "5":
        cliente = selecionar_cliente(clientes)
        if cliente:
            conta = selecionar_conta(cliente)
            if conta:
                try:
                    valor = float(input("Valor do depósito: "))
                    cliente.realizar_transacao(conta, Deposito(valor))
                except:
                    print("Valor inválido.")

    elif opcao == "6":
        cliente = selecionar_cliente(clientes)
        if cliente:
            conta = selecionar_conta(cliente)
            if conta:
                try:
                    valor = float(input("Valor do saque: "))
                    cliente.realizar_transacao(conta, Saque(valor))
                except:
                    print("Valor inválido.")

    elif opcao == "7":
        cliente = selecionar_cliente(clientes)
        if cliente:
            conta = selecionar_conta(cliente)
            if conta:
                conta.extrato()

    elif opcao == "0":
        print("Saindo...")
        break

    else:
        print("Opção inválida!")