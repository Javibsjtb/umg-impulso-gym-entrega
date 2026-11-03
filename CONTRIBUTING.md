# Colaboración del equipo

Cada integrante debe configurar su propia identidad de Git, elegir una historia del backlog, realizar cambios verificables en una rama, ejecutar pruebas y abrir un pull request. Una persona distinta debe revisar antes de integrar. No se deben fabricar commits, entrevistas, aprobaciones ni sprints.

```sh
git switch main
git pull --ff-only
git switch -c feat/US-XX-descripcion
# implementar y comprobar un cambio real
git add ruta/de/archivos
git commit -m "feat: describir cambio real"
git push -u origin feat/US-XX-descripcion
```

La plantilla de PR está en `.github/pull_request_template.md`. Las historias propuestas están en `docs/backlog.csv` y `docs/SCRUM.md`.
