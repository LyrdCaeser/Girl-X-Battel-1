# Newbie Camp — reconstrucción local, 01/10/2026

Disponible desde **Inicio → Newbie Camp** al reiniciar el servidor. Tres etapas, 30 tareas visibles y tres premios de etapa, con textos, orden y cantidades de las tablas originales. 28 tareas con seguimiento. Chat y Elite League quedan visibles como no disponibles; pueden impedir el premio de su etapa. El nivel permite abrir etapas posteriores sin eliminar tareas pendientes.

## Reglas comprobadas

Fuentes: `models/NewbieCamp.lua`, `windows/activity/NewbieCampWindow.lua`, `windows/NewbieCampListWindow.lua`, `common/tables/NewbieCampTable.lua`, `beginner_quest`, `beginner_quest_board` y textos ingleses recuperados. `tools/extract_newbie_camp.py` comprueba 10/11/9 tareas por etapa y que los tres premios ocultos coinciden con los tableros.

- Etapas 2 y 3 abiertas por nivel 30/70 **o** por completar los objetivos de la etapa anterior (`checkLockByPhase`). Completar y reclamar son condiciones distintas.
- Premio de etapa automático tras reclamar todas sus tareas visibles, siguiendo `checkAllAwardByPhase` y `reqLostAward`. Reapertura recupera un premio perdido; cada premio tiene una marca persistente independiente.
- Tablas de campaña fijan los finales de capítulos 1/5/7/10 en fases 12/52/72/102; no se supone que cada capítulo tenga diez fases.
- Texto/tipos originales distinguen las misiones Girl Lv30/Lv100 y Tests 1/10 aunque reutilicen tipo y cantidad.
- API HTTP `/api/newbie-camp/action`. Mensajes originales `GET_ROOKIE_MISSION_LIST` y `GET_ROOKIE_MISSION_AWARD`, incluidas las filas ocultas 11/21/32. Las peticiones duplicadas del premio oculto se confirman sin duplicar objetos; repetir una tarea visible reclamada se rechaza.

## Adaptaciones locales — LOCAL-079

La tarea de amistad usa los contactos locales existentes. No representa una solicitud aceptada por un jugador online. Chat y Elite League no se sustituyen por borradores ni por otra arena.

La racha registra días consecutivos del calendario local con actividad persistida, incluida abrir Camp. El primer día contado empieza con esta integración; los días históricos de acceso no permiten inferir una racha y no se inventan. Un hueco reinicia la racha actual; su máximo y los objetivos ya completados permanecen guardados. Retroceder el reloj no añade días.

La interfaz comparte el diseño local del diario, utiliza premios/iconos recuperados y ordena reclamables, pendientes y reclamadas como el modelo original. No reproduce el anuncio animado del cliente.

## Validación y relevo

Suite general: **352 pruebas aprobadas**. Después se añadieron dos casos de integración adicionales; **11 pruebas de esta ampliación aprobadas** (nueve incluidas en aquella suite, dos nuevas). Cubren fases por nivel/completitud, premios automáticos/recuperación, protocolo/rollback, reinicio, concurrencia, rachas/huecos/reloj, botones gratis/pagados, métricas de desafíos/exámenes, cofres en lote y daño Guild Boss. HTTP: script, icono y apertura responden 200; snapshot Camp 28/30, Diary 154/160. Avisos históricos de conexiones HTTP cerradas no causan fallos.

QA navegador en `validation/content-2026-10-01/qa.sqlite3`: abrir Camp, reclamar las tareas Campaña 1 y Girl Lv30, verificar Claim → Claimed, entrar en etapa 2 a nivel 30 sin completar etapa 1, reiniciar servidor temporal/recargar y comprobar marcas persistentes. Barras de progreso corregidas y captura revisada. Fuentes y partidas habituales intactas.

Pendientes: Chat y Elite League; las seis misiones de Growth Diary detalladas en `GROWTH_DIARY.md`. Siguiente prioridad: Friend Boss, Servant Training/Ulticore y Practical Work. No usar Soul Land como sustituto de Practical Work.

## Estado tras CONTENT-072

Growth Diary alcanza 157/160 métricas con Friend Boss, Training Dummy y Ulticore. Newbie Camp conserva 28/30 tareas visibles: Chat y Elite League siguen pendientes; no se sustituyen por contactos ni League ordinaria.
