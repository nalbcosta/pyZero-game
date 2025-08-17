# pyZero-game

Um pequeno jogo plataforma feito com Pygame Zero (pgzero) como projeto de exemplo.

Este repositório contém uma versão modularizada do jogo: lógica de entidades em `game/entities.py`, helpers de desenho em `game/ui.py` e o orquestrador principal em `main.py`.

Conteúdo relevante
- `main.py` - arquivo de entrada recomendado.
- `game/entities.py` - classes do jogo (Hero, Enemy, Coin).
- `game/ui.py` - funções de desenho (cenário, HUD, menus, parallax no menu).
- `images/`, `sounds/`, `music/` - pastas de assets (sprites, efeitos e trilha).

Instalação (Windows)

1. Crie um ambiente virtual (recomendado):

	 python -m venv .venv
	 .\.venv\Scripts\Activate.ps1

2. Instale dependências:

	 pip install -r requirements.txt

Como executar

Opções válidas para iniciar o jogo:

- Usando o arquivo que chama o loop do Pygame Zero (recomendado para este projeto):

	python .\main.py

- Ou, se preferir usar o utilitário do Pygame Zero:

	pgzrun main.py

Notas e dicas
- Se os sons não tocarem, verifique os nomes dos arquivos em `sounds/` e `music/`. O jogo usa aliases comuns como `hit`, `coin`, `bg_music` — ajuste os nomes dos ficheiros se necessário.
- Para ajustar o volume da música, edite a constante `MUSIC_VOLUME` em `main.py`.

Contribuições

Pull requests são bem-vindos. Para mudanças grandes, abra uma issue primeiro descrevendo a alteração.

Licença

Este projeto está sem licença explícita no repositório; adicione uma `LICENSE` se desejar torná-lo público com termos claros.

Licenças de Assets:
Digital Audio

	by  Kenney Vleugels (Kenney.nl)

			------------------------------

	License (Creative Commons Zero, CC0)
	http://creativecommons.org/publicdomain/zero/1.0/

	You may use these assets in personal and commercial projects.
	Credit (Kenney or www.kenney.nl) would be nice but is not mandatory.

			------------------------------

	Donate:   http://support.kenney.nl
	Request:  http://request.kenney.nl

	Follow on Twitter for updates:
	@KenneyNL


Music Jingles

	by  Kenney Vleugels (Kenney.nl)

			------------------------------

	License (Creative Commons Zero, CC0)
	http://creativecommons.org/publicdomain/zero/1.0/

	You may use these assets in personal and commercial projects.
	Credit (Kenney or www.kenney.nl) would be nice but is not mandatory.

			------------------------------

	Donate:   http://support.kenney.nl
	Request:  http://request.kenney.nl

	Follow on Twitter for updates:
	@KenneyNL

	
New Platformer Pack (1.0)

	Created/distributed by Kenney (www.kenney.nl)
	Creation date: 01-05-2025
	
			------------------------------

	License: (Creative Commons Zero, CC0)
	http://creativecommons.org/publicdomain/zero/1.0/

	You can use this content for personal, educational, and commercial purposes.

	Support by crediting 'Kenney' or 'www.kenney.nl' (this is not a requirement)

			------------------------------

	• Website : www.kenney.nl
	• Donate  : www.kenney.nl/donate

	• Patreon : patreon.com/kenney
	
	Follow on social media for updates:

	• Twitter:	 twitter.com/KenneyNL
	• BlueSky:	 kenney.bsky.social
	• Instagram:	 instagram.com/kenney_nl
