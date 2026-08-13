import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp


class BaixadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixador de vídeos do YouTube")
        self.root.geometry("720x480")
        self.root.minsize(600, 400)

        self.pasta_destino = r"C:\Vídeos Baixados"
        os.makedirs(self.pasta_destino, exist_ok=True)
        self.fila = queue.Queue()
        self.itens = {}
        self.rodando = True

        self._montar_interface()

        self.thread_download = threading.Thread(target=self._worker, daemon=True)
        self.thread_download.start()

        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    # ---------- Interface ----------

    def _montar_interface(self):
        topo = ttk.Frame(self.root, padding=10)
        topo.pack(fill="x")

        ttk.Label(topo, text="Cole o link do vídeo:").pack(anchor="w")

        linha_entrada = ttk.Frame(topo)
        linha_entrada.pack(fill="x", pady=(4, 0))

        self.entrada_url = ttk.Entry(linha_entrada)
        self.entrada_url.pack(side="left", fill="x", expand=True)
        self.entrada_url.bind("<Return>", lambda e: self._adicionar_url())
        self.entrada_url.focus()

        ttk.Button(linha_entrada, text="Adicionar", command=self._adicionar_url).pack(
            side="left", padx=(6, 0)
        )

        linha_pasta = ttk.Frame(topo)
        linha_pasta.pack(fill="x", pady=(8, 0))

        self.label_pasta = ttk.Label(linha_pasta, text=f"Pasta: {self.pasta_destino}")
        self.label_pasta.pack(side="left", fill="x", expand=True)

        ttk.Button(linha_pasta, text="Mudar pasta...", command=self._escolher_pasta).pack(
            side="left", padx=(6, 0)
        )

        # Tabela com a fila / status de cada vídeo
        meio = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        meio.pack(fill="both", expand=True)

        colunas = ("titulo", "status", "progresso")
        self.tabela = ttk.Treeview(meio, columns=colunas, show="headings", height=12)
        self.tabela.heading("titulo", text="Vídeo")
        self.tabela.heading("status", text="Status")
        self.tabela.heading("progresso", text="Progresso")
        self.tabela.column("titulo", width=380)
        self.tabela.column("status", width=140, anchor="center")
        self.tabela.column("progresso", width=100, anchor="center")
        self.tabela.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(meio, orient="vertical", command=self.tabela.yview)
        scroll.pack(side="right", fill="y")
        self.tabela.configure(yscrollcommand=scroll.set)

        rodape = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        rodape.pack(fill="x")
        self.label_status_geral = ttk.Label(rodape, text="Pronto. Cole um link acima e clique em Adicionar.")
        self.label_status_geral.pack(anchor="w")

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_destino if os.path.isdir(self.pasta_destino) else "C:\\")
        if pasta:
            self.pasta_destino = pasta
            self.label_pasta.config(text=f"Pasta: {self.pasta_destino}")

    def _adicionar_url(self):
        url = self.entrada_url.get().strip()
        if not url:
            return
        if not url.startswith("http"):
            messagebox.showwarning("Link inválido", "Cole um link válido do YouTube.")
            return

        item_id = self.tabela.insert("", "end", values=(url, "Na fila", "0%"))
        self.itens[item_id] = url
        self.fila.put((item_id, url, self.pasta_destino))
        self.entrada_url.delete(0, "end")
        self.label_status_geral.config(text=f"Adicionado à fila: {url}")

    def _ao_fechar(self):
        # Encerra o app; downloads em andamento na thread daemon são
        # interrompidos junto, já que a thread é daemon=True.
        pendentes = self.fila.qsize()
        if pendentes > 0:
            resposta = messagebox.askyesno(
                "Downloads pendentes",
                f"Ainda há {pendentes} vídeo(s) na fila. Fechar mesmo assim?",
            )
            if not resposta:
                return
        self.rodando = False
        self.root.destroy()

    # ---------- Download em segundo plano ----------

    def _worker(self):
        while self.rodando:
            try:
                item_id, url, pasta = self.fila.get(timeout=0.5)
            except queue.Empty:
                continue

            os.makedirs(pasta, exist_ok=True)
            self._atualizar_item(item_id, status="Baixando...", progresso="0%")

            def hook(d, item_id=item_id):
                if d["status"] == "downloading":
                    pct = d.get("_percent_str", "0%").strip()
                    self._atualizar_item(item_id, progresso=pct)
                elif d["status"] == "finished":
                    self._atualizar_item(item_id, status="Processando...", progresso="100%")

            opcoes = {
                # Prioriza H.264 (avc1), que é compatível com qualquer player,
                # incluindo o Player do Windows. Se não houver H.264 disponível
                # na resolução, cai para o melhor formato mp4 e depois qualquer um.
                "format": (
                    "bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "best[ext=mp4]/best"
                ),
                "merge_output_format": "mp4",
                "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
                "progress_hooks": [hook],
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }

            try:
                with yt_dlp.YoutubeDL(opcoes) as ydl:
                    info = ydl.extract_info(url, download=True)
                    titulo = info.get("title", url)
                self._atualizar_item(item_id, titulo=titulo, status="Concluído ✅", progresso="100%")
            except Exception as e:
                self._atualizar_item(item_id, status="Erro ❌", progresso=str(e)[:30])

            self.fila.task_done()

    def _atualizar_item(self, item_id, titulo=None, status=None, progresso=None):
        # Tkinter não é thread-safe: agenda a atualização na thread principal
        def atualizar():
            if not self.tabela.exists(item_id):
                return
            valores = list(self.tabela.item(item_id, "values"))
            if titulo is not None:
                valores[0] = titulo
            if status is not None:
                valores[1] = status
            if progresso is not None:
                valores[2] = progresso
            self.tabela.item(item_id, values=valores)

        self.root.after(0, atualizar)


def main():
    root = tk.Tk()
    app = BaixadorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()