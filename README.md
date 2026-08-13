# Baixador de Vídeos do YouTube 🎬⬇️

Um aplicativo desktop simples e eficiente, desenvolvido em Python, para baixar vídeos do YouTube de forma fácil e rápida.

A aplicação possui uma Interface Gráfica de Usuário (GUI) construída com `Tkinter` e utiliza a poderosa biblioteca `yt-dlp` para realizar os downloads. Para garantir que o aplicativo continue responsivo durante o processo, o sistema implementa processamento assíncrono em segundo plano (Threading) e uma fila de downloads.

---

## ✨ Funcionalidades

- **Interface Amigável:** Layout limpo feito com Tkinter (`ttk`), fácil de entender e usar.
- **Fila de Downloads:** Adicione múltiplos links e o aplicativo fará o download de um por vez automaticamente.
- **Processamento em Segundo Plano:** O download não "congela" a interface do usuário, graças ao uso da biblioteca `threading`.
- **Acompanhamento em Tempo Real:** Tabela interativa que mostra o nome do vídeo, status atual e a porcentagem do progresso.
- **Seleção de Diretório:** Escolha facilmente onde quer salvar seus vídeos (Padrão: `C:\Vídeos Baixados`).
- **Alta Compatibilidade:** Prioriza o formato de vídeo `H.264 (avc1)` em `.mp4`, garantindo que o vídeo rode perfeitamente no Player nativo do Windows e em dispositivos móveis.
- **Prevenção de Perdas:** Alerta caso o usuário tente fechar o aplicativo enquanto ainda há downloads pendentes na fila.

---

## 🚀 Pré-requisitos

Antes de começar, você precisará ter o **Python 3.7+** instalado em sua máquina. Além disso, é necessário instalar as seguintes dependências:

1. **Biblioteca Python:**
   ```bash
   pip install yt-dlp
   ```

2. **FFmpeg:**
   O `yt-dlp` depende do FFmpeg para juntar áudio e vídeo em alta qualidade. Certifique-se de baixá-lo e adicioná-lo ao `PATH` do seu sistema operacional.

---

## 🛠️ Como Instalar e Executar

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/Iago1610/InstaladorDeVideosYT.git
   cd InstaladorDeVideosYT
   ```

2. **Instale as dependências** (conforme listado nos pré-requisitos).

3. **Execute o aplicativo:**
   ```bash
   python main.py
   ```
   *(Substitua `main.py` pelo nome exato do arquivo do script.)*

---

## 💻 Como Usar

1. Ao abrir o aplicativo, copie o link de um vídeo do YouTube.
2. Cole o link na barra de texto superior.
3. Clique no botão **"Adicionar"** ou pressione a tecla **Enter**.
4. *(Opcional)* Clique em **"Mudar pasta..."** para escolher onde o arquivo será salvo.
5. Acompanhe o status e a barra de progresso na tabela central até aparecer **"Concluído ✅"**.

---

## 🏗️ Arquitetura do Código

- **Tkinter / ttk:** Responsável pela construção da interface gráfica (janela, botões, tabela Treeview).
- **yt-dlp:** Motor de extração e download do YouTube (sucessor do popular `youtube-dl`).
- **`queue.Queue` e `threading`:** Trabalham em conjunto no método `_worker`. A thread principal lida exclusivamente com a interface (mantendo-a fluida), enquanto uma thread "operária" (daemon) aguarda itens na fila e processa o download remotamente usando a API do `yt-dlp`. O método `after()` do Tkinter é usado para atualizar a barra de progresso de forma thread-safe.

---

## ⚠️ Aviso Legal

Este software foi criado estritamente para fins educacionais. O download de vídeos do YouTube pode violar os Termos de Serviço da plataforma. Certifique-se de ter o direito de baixar o conteúdo (como vídeos de sua própria autoria, de domínio público, ou com a devida permissão). O uso indevido da ferramenta é de total responsabilidade do usuário.

---

## 📄 Licença

Este projeto é de código aberto e está sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.
