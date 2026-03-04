import customtkinter as ctk
import threading
import time
import imaplib
import email
import os
import re
import json
import datetime
import webbrowser
from email.header import decode_header
from cryptography.fernet import Fernet

# Configurações Globais
PADRAO_REGEX = r"^\d{2}\.\d{2}\s[A-Z\s]+\sNF\s\d+"
ARQUIVO_DADOS = "vault.json"
CHAVE_FILE = "secret.key"
PASTA_DESTINO = "triagem_notas"

class SecurityManager:
    @staticmethod
    def get_key():
        if not os.path.exists(CHAVE_FILE):
            key = Fernet.generate_key()
            with open(CHAVE_FILE, "wb") as f: f.write(key)
        return open(CHAVE_FILE, "rb").read()

    @classmethod
    def encrypt(cls, texto):
        if not texto: return ""
        f = Fernet(cls.get_key())
        return f.encrypt(texto.encode()).decode()

    @classmethod
    def decrypt(cls, texto_cifrado):
        if not texto_cifrado: return ""
        f = Fernet(cls.get_key())
        try: return f.decrypt(texto_cifrado.encode()).decode()
        except: return ""

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TB System | Versão 2026")
        self.geometry("1100x800")
        ctk.set_appearance_mode("Dark")
        
        self.contas = self.carregar_dados()
        self.monitorando = False
        
        self.setup_ui()
        self.log("🛡️ TB System inicializado com sucesso.")
        self.log("Status: Pronto para processamento de Notas Fiscais.")

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TB SYSTEM", font=("Segoe UI", 24, "bold"), text_color="#3b8ed0").pack(pady=(30, 20))

        self.btn_toggle = ctk.CTkButton(self.sidebar, text="INICIAR TRIAGEM", height=45, 
                                         fg_color="#2ecc71", hover_color="#27ae60", 
                                         font=("Segoe UI", 14, "bold"), command=self.toggle_engine)
        self.btn_toggle.pack(pady=10, padx=20, fill="x")

        self.btn_folder = ctk.CTkButton(self.sidebar, text="ABRIR PASTA NF", height=35, 
                                         fg_color="#34495e", command=self.abrir_pasta)
        self.btn_folder.pack(pady=10, padx=20, fill="x")

        self.status_indicator = ctk.CTkLabel(self.sidebar, text="● Sistema em Espera", text_color="#e74c3c")
        self.status_indicator.pack(pady=5)

        # --- Abas ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tab_dash = self.tabview.add("Painel de Controle")
        self.tab_config = self.tabview.add("Contas de Email")
        self.tab_filtros = self.tabview.add("Lista de Fornecedores")

        self.setup_tab_dash()
        self.setup_tab_config()
        self.setup_tab_filtros()

    def setup_tab_dash(self):
        self.log_view = ctk.CTkTextbox(self.tab_dash, font=("Consolas", 12), state="disabled", fg_color="#1a1a1a")
        self.log_view.pack(expand=True, fill="both", padx=10, pady=10)

    def setup_tab_config(self):
        f_add = ctk.CTkFrame(self.tab_config)
        f_add.pack(fill="x", padx=10, pady=10)
        self.ent_email = ctk.CTkEntry(f_add, placeholder_text="E-mail", width=250)
        self.ent_email.grid(row=0, column=0, padx=5, pady=10)
        self.ent_pass = ctk.CTkEntry(f_add, placeholder_text="Senha de App", show="*", width=200)
        self.ent_pass.grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkButton(f_add, text="Conectar", width=100, command=self.add_conta).grid(row=0, column=2, padx=5)

        self.scroll_contas = ctk.CTkScrollableFrame(self.tab_config, height=400)
        self.scroll_contas.pack(fill="both", expand=True, padx=10, pady=5)
        self.renderizar_contas()

    def setup_tab_filtros(self):
        f_add = ctk.CTkFrame(self.tab_filtros)
        f_add.pack(fill="x", padx=10, pady=10)
        self.ent_forn = ctk.CTkEntry(f_add, placeholder_text="fornecedor@exemplo.com.br", width=400)
        self.ent_forn.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        ctk.CTkButton(f_add, text="Cadastrar", width=100, command=self.add_filtro).pack(side="left", padx=10)

        self.scroll_forn = ctk.CTkScrollableFrame(self.tab_filtros, height=400)
        self.scroll_forn.pack(fill="both", expand=True, padx=10, pady=5)
        self.renderizar_fornecedores()

    def log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log_view.configure(state="normal")
        self.log_view.insert("end", f"[{ts}] {msg}\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    # --- Lógica de Renderização e Ações ---
    def renderizar_contas(self):
        for widget in self.scroll_contas.winfo_children(): widget.destroy()
        for i, conta in enumerate(self.contas["minhas_contas"]):
            frame = ctk.CTkFrame(self.scroll_contas)
            frame.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(frame, text=f"📧 {conta['user']}", anchor="w").pack(side="left", padx=10, expand=True, fill="x")
            ctk.CTkButton(frame, text="🗑️", width=30, fg_color="#e74c3c", command=lambda idx=i: self.remover_conta(idx)).pack(side="left", padx=2)

    def renderizar_fornecedores(self):
        for widget in self.scroll_forn.winfo_children(): widget.destroy()
        for i, forn in enumerate(self.contas["fornecedores"]):
            frame = ctk.CTkFrame(self.scroll_forn)
            frame.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(frame, text=f"🎯 {forn}", anchor="w").pack(side="left", padx=10, expand=True, fill="x")
            ctk.CTkButton(frame, text="🗑️", width=30, fg_color="#e74c3c", command=lambda idx=i: self.remover_filtro(idx)).pack(side="right", padx=10)

    def add_conta(self):
        e, p = self.ent_email.get().strip(), self.ent_pass.get().strip()
        if e and p:
            self.contas["minhas_contas"].append({"user": e, "pass": SecurityManager.encrypt(p)})
            self.salvar_dados(); self.renderizar_contas()
            self.ent_email.delete(0, 'end'); self.ent_pass.delete(0, 'end')
            self.log(f"✅ Conta {e} integrada ao TB System.")

    def remover_conta(self, index):
        self.contas["minhas_contas"].pop(index)
        self.salvar_dados(); self.renderizar_contas()

    def add_filtro(self):
        f = self.ent_forn.get().strip().lower()
        if f and f not in self.contas["fornecedores"]:
            self.contas["fornecedores"].append(f)
            self.salvar_dados(); self.renderizar_fornecedores()
            self.ent_forn.delete(0, 'end')
            self.log(f"🎯 Monitorando fornecedor: {f}")

    def remover_filtro(self, index):
        self.contas["fornecedores"].pop(index)
        self.salvar_dados(); self.renderizar_fornecedores()

    def abrir_pasta(self):
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        webbrowser.open(os.path.realpath(PASTA_DESTINO))

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
            except: pass
        return {"minhas_contas": [], "fornecedores": []}

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w") as f: json.dump(self.contas, f)

    def toggle_engine(self):
        self.monitorando = not self.monitorando
        if self.monitorando:
            self.btn_toggle.configure(text="PARAR TRIAGEM", fg_color="#e74c3c")
            self.status_indicator.configure(text="● TB System Ativo", text_color="#2ecc71")
            self.log("🚀 Iniciando varredura cíclica...")
            threading.Thread(target=self.main_loop, daemon=True).start()
        else:
            self.btn_toggle.configure(text="INICIAR TRIAGEM", fg_color="#2ecc71")
            self.status_indicator.configure(text="● TB System Pausado", text_color="#e74c3c")
            self.log("🛑 Varredura encerrada.")

    def main_loop(self):
        while self.monitorando:
            for conta in self.contas["minhas_contas"]:
                if not self.monitorando: break
                self.processar_caixa(conta)
            if self.monitorando: time.sleep(45)

    def processar_caixa(self, conta):
        try:
            user = conta["user"]; pw = SecurityManager.decrypt(conta["pass"])
            server = "imap.gmail.com" if "@gmail" in user else "outlook.office365.com"
            mail = imaplib.IMAP4_SSL(server)
            mail.login(user, pw); mail.select("inbox")
            _, data = mail.search(None, "UNSEEN")
            for num in data[0].split():
                _, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                from_header = msg.get("From")
                nome_rem, email_rem = email.utils.parseaddr(from_header)
                if email_rem.lower() in self.contas["fornecedores"]:
                    self.triar_anexos(msg, nome_rem if nome_rem else email_rem)
            mail.logout()
        except Exception: pass

    def triar_anexos(self, msg, remetente):
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        for part in msg.walk():
            if "attachment" in str(part.get("Content-Disposition")):
                nome_arq = self.decodificar_nome(part.get_filename())
                if nome_arq and re.search(PADRAO_REGEX, nome_arq.upper()):
                    caminho = os.path.join(PASTA_DESTINO, nome_arq)
                    
                    if os.path.exists(caminho):
                        self.log(f"⚠️ AVISO: '{nome_arq}' já existe no TB System (Origem: {remetente})")
                        continue
                        
                    with open(caminho, "wb") as f: f.write(part.get_payload(decode=True))
                    self.log(f"✅ NF BAIXADA: {nome_arq} | Fornecedor: {remetente}")

    def decodificar_nome(self, n):
        if not n: return None
        try:
            dec = decode_header(n)[0]
            if isinstance(dec[0], bytes): return dec[0].decode(dec[1] or 'utf-8')
            return dec[0]
        except: return n

if __name__ == "__main__":
    App().mainloop()