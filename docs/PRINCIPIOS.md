# Principios del proyecto

> Estos son los principios que rigen las decisiones del proyecto. Cuando
> haya duda, vuelve aquí.

---

## 1. Simplicidad antes que sofisticación

Usa la herramienta más simple que resuelva bien el problema. No metas
dependencias, abstracciones ni capas que se justifiquen con un "por si
acaso".

Si una librería estándar de Python o las que ya están instaladas
resuelven el caso, no añadas nada nuevo. Si una función de 20 líneas
hace el trabajo, no la conviertas en una clase con cinco métodos.

Cuando dudes entre una solución clara y una sofisticada, elige la clara.
Sofisticación bajo demanda, no por defecto.

---

## 2. El observador no programa

El usuario final del sistema es un observador de fauna que no programa.
Cualquier interacción humana con el sistema debe ser:

- Pegar un texto en algún sitio
- Subir un archivo a una carpeta
- Pinchar un botón en un dashboard
- Escribir en una celda de la interfaz web de Supabase

Nunca: escribir código Python, escribir SQL, editar archivos de
configuración, ejecutar comandos en terminal.

Si una funcionalidad del sistema no se puede usar sin tocar código, está
mal diseñada. Replantéala.

---

## 3. Los datos son sagrados

Los datos que el observador ha recogido son el activo más valioso del
proyecto. Cualquier operación que pueda destruirlos requiere:

- Que sea explícita (el usuario lo ha pedido en la sesión actual).
- Que esté limitada (al ámbito mínimo necesario, no más).
- Que sea reversible si es posible (backup previo).

Operaciones que requieren confirmación explícita: borrar filas, vaciar
tablas, sobrescribir archivos del usuario, resetear catálogos.

**Cada inserción significativa dispara un backup automático**. Antes de
una operación destructiva, comprobar que existe un backup reciente
(menos de 24 horas).

---

## 4. Dev y prod están separados

Hay dos entornos Supabase: `fauna-dev` (desarrollo y pruebas) y
`fauna-prod` (datos reales). Esto se respeta sin excepciones.

- Los tests siempre apuntan a dev (o a una BD local mockeada).
- El desarrollo siempre apunta a dev.
- El paso a prod es explícito, lo dispara el usuario con una decisión
  consciente.

---

## 5. La bitácora es la memoria del proyecto

`docs/BITACORA.md` es donde vive el estado del proyecto entre sesiones
y entre agentes. Si algo no está en la bitácora, no existe a efectos
prácticos: el siguiente agente no lo verá.

Por eso:

- Las tareas completadas se marcan en bitácora.
- Las decisiones técnicas importantes van a `docs/DECISIONES.md`.
- El cierre de sesión actualiza la bitácora.
- Los handoffs entre agentes se documentan en bitácora.

No confíes en la memoria de la conversación: confía en el archivo.

---

## 6. Los secretos no entran en git

Bajo ninguna circunstancia. Las credenciales viven en `.env` (en local)
y nada que pueda comprometer al sistema o al observador llega al repo.

Antes de cualquier commit, se verifica el diff (ver `docs/SEGURIDAD.md`).
Si hay sospecha de que algo sensible está incluido, se detiene el
commit y se avisa al usuario.

Esta regla aplica también al repositorio privado: aunque sea privado,
no es seguro depositar secretos en él.
