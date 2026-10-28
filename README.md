# Performance Monitor

O **Performance Monitor** é uma aplicação desktop desenvolvida em Python, com interface gráfica em **PySide6**, criada para estudar como um programa pode aparentar uma finalidade legítima e executar um comportamento diferente do esperado — uma característica associada a cavalos de Troia (trojans).

A interface apresenta um menu de diagnóstico de componentes do computador. Ao iniciar a análise, o aplicativo exibe progresso simulado, interrompe a sequência com um alerta fictício de comprometimento e abre janelas reproduzindo Bad Apple. A mensagem também revela que se trata de uma pegadinha.

## Objetivo do projeto

Explorar o desenvolvimento de aplicações desktop e compreender, por meio de uma simulação local, conceitos de disfarce de funcionalidade e engenharia social associados a trojans. O projeto também exercita programação orientada a objetos, eventos de interface, tarefas em segundo plano, criptografia de recursos e distribuição de executáveis para Windows.

O aplicativo não implementa acesso remoto, coleta de credenciais, exfiltração, persistência ou propagação. O diagnóstico é visual e simulado: não mede o desempenho nem verifica a saúde dos componentes. A criptografia é aplicada ao vídeo distribuído com o programa, não aos arquivos do usuário.

## Funcionalidades

- Seleção de processador, memória RAM, placa de vídeo ou armazenamento.
- Preparação do vídeo em uma thread separada e barra de progresso simulada.
- Alerta fictício de invasão, com revelação da pegadinha.
- Janelas de vídeo surgindo a cada 150 ms em posições aleatórias.
- Limite de 12 janelas simultâneas; depois disso, reutiliza as existentes em novas posições.
- Reprodução em loop, com áudio em apenas uma janela.
- Encerramento de toda a aplicação por `Esc` com uma janela do app em foco, ao fechar qualquer janela ou automaticamente 45 segundos após o alerta.

A reprodução simultânea consome CPU, memória e GPU; o limite de janelas reduz o crescimento do consumo, mas não garante desempenho em qualquer computador. Use a simulação em máquinas próprias ou com autorização dos participantes.

## Tecnologias utilizadas

| Tecnologia | Uso |
| --- | --- |
| Python | Lógica e organização orientada a objetos |
| PySide6 / Qt | Interface gráfica, eventos e reprodução de áudio e vídeo |
| cryptography | Criptografia autenticada AES-256-GCM do recurso de vídeo |
| PyInstaller | Empacotamento em um executável para Windows |
| GitHub Actions | Build no Windows e publicação de releases |

## Executar no Windows

Com Python de 64 bits instalado, coloque `bad-apple.mp4` na raiz do projeto. Prefira um MP4 com vídeo H.264 e áudio AAC. No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Em desenvolvimento, o programa lê o MP4 diretamente. As dependências estão declaradas em `requirements.txt`.

## Gerar o executável

Execute o build no Windows:

```powershell
.\.venv\Scripts\python.exe build.py
```

Para usar outro arquivo:

```powershell
.\.venv\Scripts\python.exe build.py --video 'C:\Videos\bad-apple.mp4'
```

O resultado é `dist\PcDiagnostic.exe`. O executável inclui o interpretador Python, as bibliotecas necessárias e o vídeo criptografado. O destinatário não precisa instalar Python. O empacotamento em arquivo único extrai bibliotecas temporárias ao iniciar; não significa execução inteiramente em memória.

### Releases pelo GitHub Actions

O workflow `.github/workflows/release.yml` executa em Windows x64 com Python 3.12. Ele pode ser iniciado manualmente pela aba **Actions** ou pelo envio de uma tag `v*`.

Como os arquivos `*.mp4` são ignorados pelo Git, informe uma URL HTTPS direta no campo `video_url` da execução manual ou configure a variável de repositório `BAD_APPLE_VIDEO_URL` em **Settings → Secrets and variables → Actions → Variables**.

O workflow baixa o vídeo, verifica a sintaxe e a criptografia, gera o executável e publica uma release com `PcDiagnostic.exe` e `SHA256SUMS.txt`. Também salva esses arquivos como artifact por 14 dias. Em execuções manuais, a tag da release é gerada a partir do identificador e da tentativa da execução.

## Criptografia e limites de proteção

Durante o build, são gerados uma chave AES de 256 bits e um nonce aleatório. O vídeo é criptografado com AES-GCM e incorporado ao executável junto com a chave. Isso evita distribuir um MP4 separado, mas **não impede extração por engenharia reversa**, pois o aplicativo precisa ter acesso à chave.

Na versão empacotada, o vídeo é descriptografado antes da reprodução para `%TEMP%\PcDiagnostic-<identificador>\playback.mp4`. O conteúdo pode ser acessado nesse local durante a execução. O programa tenta removê-lo ao encerrar normalmente; interrupções forçadas ou arquivos ainda abertos podem deixar resíduos.

A implementação atual lê o vídeo inteiro em memória durante a criptografia e a descriptografia. A URL de origem também permanece pública se o arquivo estiver em uma hospedagem pública. O recurso não é proteção contra extração nem mecanismo de evasão de ferramentas de segurança.

## Estrutura

- `app.py`: interface, preparação, reprodução e encerramento.
- `media.py`: criptografia e formato do recurso de vídeo.
- `build.py`: preparação dos recursos e empacotamento.
- `build.ps1`: atalho opcional para o build no PowerShell.
- `tests/test_media.py`: testes de integridade e descriptografia.
- `.github/workflows/release.yml`: build e publicação no GitHub.

## Validação

Para executar os testes de criptografia:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes cobrem recuperação do conteúdo original e rejeição de dados adulterados, chave incorreta e formato inválido. Eles não validam a reprodução nem a interface.

A sintaxe e os testes de criptografia foram verificados no ambiente Linux de desenvolvimento. O comportamento visual e o executável precisam ser validados no Windows, incluindo saída por Esc, fechamento de janelas, limite de 45 segundos e limpeza dos temporários.
