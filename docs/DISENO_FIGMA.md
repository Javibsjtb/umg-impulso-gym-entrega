# Diseño y atribución

Referencia elegida por el usuario: [Chamith Fitness Center Gym Web Template (Community)](https://www.figma.com/design/HvcxdHqNuFoNFAI8WtUpTg/Chamith-Fitness-Center-Gym-Web-Template--Community-?node-id=0-1).

Se inspeccionó la página 0:1 y se obtuvo contexto visual de los nodos 1:38 (hero), 1:91 (beneficios), 1:136 (entrenamiento), 1:149 (galería), 1:163 (precios) y 1:366 (pie). La adaptación conserva fotografías, emblema, iconos, tipografía Rubik, composición negra/blanca y tarjetas de precio. Los textos están en español y los precios se consultan de la base relacional. El panel interno adapta esos colores y fotografía a las tareas administrativas.

Los archivos exportados están en `static/gym/figma/`, se sirven localmente y no dependen de enlaces temporales. No se usa una captura del diseño como página. Rubik proviene de google/fonts; su licencia OFL está junto a la fuente.

La sección de opiniones no se reproduce: no existen testimonios reales. Fotografías, emblema y nombre de demostración no acreditan instalaciones, personal o negocio real. Antes del uso comercial, confirmar los derechos de la plantilla y sus fotografías y sustituir el emblema por la marca autorizada. No se presume una licencia comercial por estar en Community.

Configuración: `GYM_NAME`, `GYM_PHONE` y `DEMO_MODE`. Modificar los planes desde la administración. El teléfono debe tener prefijo internacional. La portada es pública; socios, pagos, reportes y asistencia requieren sesión y rol.

Evidencia visual: [escritorio](evidencias/portada-desktop.png), [móvil](evidencias/portada-mobile.png), [panel](evidencias/panel-desktop.png), [panel móvil](evidencias/panel-mobile.png).

## Refinamiento de interfaz (octubre 2026)

Las capas `static/gym/refine.css` (panel) y `static/gym/fitness-refine.css` (portada) se cargan después de los estilos base y conservan la identidad Chamith: negro/blanco, Rubik y acento rojo. Cambios principales:

- Iconos SVG propios en `static/gym/icons.svg`, usados con `{% icon 'nombre' %}` en lugar de caracteres Unicode.
- Texto mínimo de 11–12 px y grises con contraste AA; anillo de foco neutro en lugar del verde heredado.
- Tablas que en móvil se convierten en filas apiladas con etiqueta, sin columnas cortadas.
- Menú lateral móvil con fondo oscurecido, botón de cierre, Escape y retorno de foco.
- Respuesta táctil en botones (escala 0.97), transiciones de 140–260 ms con curva ease-out, hover solo en dispositivos con puntero y respeto a `prefers-reduced-motion`.
- Franja de datos de la portada calculada desde los planes activos (cantidad, precio desde, días de vigencia).
- Corrección de las opciones «Activos» y «En período vigente», que no aparecían en los filtros por etiquetas mal cerradas.
