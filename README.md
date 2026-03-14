# TB System - Triagem Automática de NF

Um sistema desktop em Python com interface `customtkinter` para monitorar e triagem automática de notas fiscais recebidas por e-mail.

## O que este sistema faz

- Conecta a contas de e-mail IMAP (Gmail/Outlook etc.)
- Busca e-mails não lidos
- Valida se o remetente é um fornecedor cadastrado
- Lê e processa anexos com nome que corresponde ao padrão de NF
- Salva arquivos de NF em pastas de triagem definidas por regras (por exemplo, `SCP`, `ADM`)
- Exibe dashboard com métricas (NFs processadas, erros, contas e fornecedores)
- Mantém dados criptografados localmente (`vault.json` com senha cifrada, `secret.key` para Fernet)

## Tecnologias usadas

- Python 3
- `customtkinter` para GUI moderna
- `imaplib` para IMAP
- `email` para processar mensagens
- `cryptography.fernet` para cifrar senhas
- `PIL` (Pillow) para imagens (usado na interface)

## Arquivos principais

- `tbsystem.py`: aplicação principal
- `vault.json`: arquivo de dados locais (contas e fornecedores)
- `secret.key`: chave Fernet para criptografia de senhas
- `dist/`: executáveis gerados após build

## Como usar

### Usando o TB System

1. Abra a pasta `dist` e execute `tbsystem.exe` (ou o nome do EXE criado).
2. No aplicativo, cadastre uma conta de e-mail (use senha de app).
3. Cadastre fornecedores (e-mails) para filtrar NF.
4. Clique em `▶ INICIAR TRIAGEM`.
5. As NF serão salvas em `RAIZ_TRIAGEM` configurado em `tbsystem.py`.

## Configuração adicional

- Altere `RAIZ_TRIAGEM` em `tbsystem.py` para a pasta de destino desejada.
- O padrão de nome de NF está em `PADRAO_REGEX`, ajustável para seu formato.

## Segurança

- Não compartilhe `secret.key` nem `vault.json` com terceiros.
- Use senhas de app (não senha padrão) para Gmail/Outlook.

## Observações

- Os dados de login são armazenados cifrados, mas a chave de cifragem fica em `secret.key` local.
- A triagem depende de formatos de nome de anexos e regras estáticas. Ajuste o código para outras pastas.
