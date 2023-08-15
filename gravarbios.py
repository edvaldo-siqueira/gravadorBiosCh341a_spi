import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os

class BiosFlashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicativo de Atualização de BIOS")
        self.root.geometry("400x300")  # Definindo o tamanho da janela
        
        self.criar_widgets()

    def criar_widgets(self):
        self.botao_backup = tk.Button(self.root, text="Fazer Backup da BIOS", command=self.backup_bios, bg="yellow")
        self.botao_apagar = tk.Button(self.root, text="Apagar BIOS", command=self.apagar_bios, bg="green", state="disabled")
        self.botao_gravar = tk.Button(self.root, text="Gravar BIOS", command=self.gravar_bios, bg="red")
        
        self.botao_backup.pack(pady=20)
        self.botao_apagar.pack(pady=20)
        self.botao_gravar.pack(pady=20)
        
    def executar_flashrom(self, comando):
        try:
            saida = subprocess.check_output(comando, stderr=subprocess.STDOUT, shell=True)
            return saida.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return e.output.decode("utf-8")
        
    def exibir_mensagem(self, titulo, mensagem):
        messagebox.showinfo(titulo, mensagem)
        
    def backup_bios(self):
        caminho_salvar = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Arquivos BIOS", "*.bin")])
        if caminho_salvar:
            thread = threading.Thread(target=self.realizar_backup, args=(caminho_salvar,))
            thread.start()
        
    def realizar_backup(self, caminho_salvar):
        resultado = self.executar_flashrom(f"flashrom -p ch341a_spi -r {caminho_salvar}")
        if "Reading flash... done." in resultado:
            tamanho_arquivo_bits = os.path.getsize(caminho_salvar) * 8  # Tamanho em bits
            tamanho_arquivo_mbits = tamanho_arquivo_bits / (1024 * 1024)  # Tamanho em Mbits
            self.exibir_mensagem("Backup Bios OK!", f"O backup da BIOS foi concluído com sucesso.\nTamanho do arquivo: {tamanho_arquivo_mbits:.2f} Mbits.")
            self.botao_apagar["state"] = "normal"  # Habilitar o botão de apagar após o backup
            
    def apagar_bios(self):
        thread = threading.Thread(target=self.realizar_apagamento)
        thread.start()
        
    def realizar_apagamento(self):
        resultado = self.executar_flashrom("flashrom -p ch341a_spi -E")
        if "Erasing..." in resultado and "VERIFIED" in resultado:
            self.exibir_mensagem("Bios Apagada com sucesso!", "A BIOS foi apagada com sucesso.")
        else:
            self.exibir_mensagem("Falha ao Apagar a BIOS", "O apagamento da BIOS falhou.")
        
    def gravar_bios(self):
        arquivo_selecionado = filedialog.askopenfilename(filetypes=[("Arquivos BIOS", "*.bin")])
        if arquivo_selecionado:
            thread = threading.Thread(target=self.realizar_gravacao, args=(arquivo_selecionado,))
            thread.start()
        
    def realizar_gravacao(self, arquivo_selecionado):
        resultado = self.executar_flashrom(f"flashrom -p ch341a_spi -w {arquivo_selecionado}")
        if "Verifying flash..." in resultado:
            if "VERIFIED" in resultado:
                self.exibir_mensagem("Bios gravada OK!", "A gravação da BIOS foi concluída com sucesso.")
            else:
                self.exibir_mensagem("Bios Falhou!", "A gravação da BIOS falhou.")
        else:
            self.exibir_mensagem("Bios Falhou!", "A gravação da BIOS falhou.")

if __name__ == "__main__":
    raiz = tk.Tk()
    app = BiosFlashApp(raiz)
    raiz.mainloop()
