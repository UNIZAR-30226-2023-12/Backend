Esta configuración de redis funciona en Ubuntu, en Windows con Ubuntu en WSL ha dado problemas (puede que sea culpa de los finales de linea en los ficheros).

Para construir e iniciar el servidor Redis con claves artificiales pobladas por defecto, ejecutar start.sh

Para eliminar el contenedor, ejecutar rm.sh

Para ejecutar redis-cli con la autenticación necesaria, ejecutar cli.sh. El script está preparado para pasar a redis-cli argumentos, con el fin de automatizar inserciones. Es decir, que se puede insertar la orden "SET idUltimoUsuario 0" directamente en Redis (a través de redis-cli, y usando el usuario del sistema melodia), mediante el comando

```bash
./cli.sh SET idUltimoUsuario 0
```

La población realizada por defecto se encuentra en el fichero populate.sh.
