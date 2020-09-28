# Alasala Island

Game for PyWeek 30 - Castaway!

In this game you suffer a shipwreck and find yourself on the mysterious
Alasala Island. Can you escape or will you succumb to the temptation to
stay forever?

We may add small bug fixes on `master`. [Compare `master` against the `pyweek` tag.](https://github.com/darabos/alasala/compare/pyweek...master)

This games uses a Web UI. You need flask:

```bash
pip install Flask
```

After that, run the game with:
```bash
./run_game.sh
```

To reset the game, just delete the file called `db`.

Once the server is up, just direct your browser to:
http://localhost:5000
