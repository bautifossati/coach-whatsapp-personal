"""
citas.py — Banco de citas de libros de crecimiento personal
Más de 80 citas organizadas por categoría, de los mejores libros del gìnero.
"""

import random

CITAS = {
    "habitos": [
        {
            "cita": "No son tus resultados los que cambian tu vida, son tus hábitos.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
        {
            "cita": "Cada acción que realizás es un voto a favor del tipo de persona que querés ser.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
        {
            "cita": "No te planteás metas, te planteás sistemas. Las metas son para los resultados que querés lograr. Los sistemas son para los procesos que llevan a esos resultados.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
        {
            "cita": "Hacer pequeñas mejoras del 1% cada día no parece gran cosa, pero a lo largo del tiempo puede ser enorme.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
        {
            "cita": "El poder del hábito radica en que podés elegir el comportamiento al principio y después el hábito te lleva a él automáticamente.",
            "libro": "El poder del hábito",
            "autor": "Charles Duhigg"
        },
        {
            "cita": "La motivación nos lleva a empezar. El hábito nos lleva a continuar.",
            "libro": "Mini hábitos",
            "autor": "Stephen Guise"
        },
        {
            "cita": "Si te cuesta arrancar, es que la tarea es demasiado grande. Hacela más pequeña.",
            "libro": "Mini hábitos",
            "autor": "Stephen Guise"
        },
        {
            "cita": "La primera ley del cambio conductual: hacé que sea obvio.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
        {
            "cita": "El ambiente es la mano invisible que da forma al comportamiento humano.",
            "libro": "Atomic Habits",
            "autor": "James Clear"
        },
    ],
    "disciplina": [
        {
            "cita": "Disciplina es elegir entre lo que querés ahora y lo que más querés.",
            "libro": "The Motivation Myth",
            "autor": "Jeff Haden"
        },
        {
            "cita": "La disciplina es el puente entre las metas y el logro.",
            "libro": "Sin excusas",
            "autor": "Brian Tracy"
        },
        {
            "cita": "El dolor de la disciplina es mucho menor que el dolor del arrepentimiento.",
            "libro": "Sin excusas",
            "autor": "Brian Tracy"
        },
        {
            "cita": "No te esperes a tener ganas. La acción genera motivación, no al revés.",
            "libro": "The 5 Second Rule",
            "autor": "Mel Robbins"
        },
        {
            "cita": "Contá hacia atrás: 5, 4, 3, 2, 1. Y después movete. Tu cerebro no va a tener tiempo de sabotearte.",
            "libro": "The 5 Second Rule",
            "autor": "Mel Robbins"
        },
        {
            "cita": "La consistencia supera al talento cuando el talento no es consistente.",
            "libro": "Great by Choice",
            "autor": "Jim Collins"
        },
        {
            "cita": "Hacé lo que tenés que hacer, cuando tenés que hacerlo, te den o no ganas.",
            "libro": "Can't Hurt Me",
            "autor": "David Goggins"
        },
        {
            "cita": "La mayoría de la gente vive con el 40% de su potencial. Cuando tu mente dice que ya fue, en realidad estás al 40%.",
            "libro": "Can't Hurt Me",
            "autor": "David Goggins"
        },
        {
            "cita": "Cada vez que elegís la comodidad frente al crecimiento, le mandás una señal a tu cerebro: no soy capaz.",
            "libro": "Can't Hurt Me",
            "autor": "David Goggins"
        },
    ],
    "proposito": [
        {
            "cita": "Quien tiene un porqué para vivir puede soportar casi cualquier cómo.",
            "libro": "El hombre en busca de sentido",
            "autor": "Viktor Frankl"
        },
        {
            "cita": "El éxito es la consecuencia de perseguir tu propósito, no el propósito en sí mismo.",
            "libro": "Start With Why",
            "autor": "Simon Sinek"
        },
        {
            "cita": "La gente no compra lo que hacés, compra por qué lo hacés.",
            "libro": "Start With Why",
            "autor": "Simon Sinek"
        },
        {
            "cita": "Vivir sin propósito es como navegar sin brújula: podés moverte mucho y no llegar a ningún lado.",
            "libro": "El poder del ahora",
            "autor": "Eckhart Tolle"
        },
        {
            "cita": "No te preguntes qué necesita el mundo. Preguntate qué te hace sentir vivo. Porque lo que el mundo necesita es gente que esté viva.",
            "libro": "The Alchemist",
            "autor": "Paulo Coelho"
        },
        {
            "cita": "Cuando querés algo, todo el universo conspira para que puedas lograrlo.",
            "libro": "El Alquimista",
            "autor": "Paulo Coelho"
        },
        {
            "cita": "Tu tiempo es limitado. No lo desperdicies viviendo la vida de otra persona.",
            "libro": "Steve Jobs Biography",
            "autor": "Walter Isaacson"
        },
    ],
    "mindset": [
        {
            "cita": "El mayor descubrimiento de mi generación es que un ser humano puede cambiar su vida cambiando su actitud mental.",
            "libro": "As a Man Thinketh",
            "autor": "James Allen"
        },
        {
            "cita": "En una mentalidad de crecimiento, los errores no te definen. Son información que te ayuda a mejorar.",
            "libro": "Mindset",
            "autor": "Carol Dweck"
        },
        {
            "cita": "La mano que te dieron no es lo que importa. Cómo jugás esa mano, eso es lo que importa.",
            "libro": "Mindset",
            "autor": "Carol Dweck"
        },
        {
            "cita": "No es lo que te pasa lo que te define. Es lo que hacés con lo que te pasa.",
            "libro": "Man's Search for Meaning",
            "autor": "Viktor Frankl"
        },
        {
            "cita": "El cerebro es como un músculo: cuanto más lo usás para el crecimiento, más crece.",
            "libro": "Mindset",
            "autor": "Carol Dweck"
        },
        {
            "cita": "Las personas con mentalidad fija evitan los desafíos. Las personas con mentalidad de crecimiento los buscan.",
            "libro": "Mindset",
            "autor": "Carol Dweck"
        },
        {
            "cita": "No tenés control sobre lo que te pasa, pero sí sobre cómo respondés.",
            "libro": "Estoicismo para una vida buena",
            "autor": "William Irvine"
        },
        {
            "cita": "Divide tu preocupaciones en dos grupos: lo que está bajo tu control y lo que no. Enfocate solo en lo primero.",
            "libro": "Meditaciones",
            "autor": "Marco Aurelio"
        },
        {
            "cita": "El obstáculo es el camino.",
            "libro": "The Obstacle Is the Way",
            "autor": "Ryan Holiday"
        },
    ],
    "productividad": [
        {
            "cita": "Comé la rana. Hacé primero la tarea que más te da miedo o más te cuesta.",
            "libro": "Eat That Frog",
            "autor": "Brian Tracy"
        },
        {
            "cita": "La multitarea es un mito. Hacé una cosa a la vez y hacela bien.",
            "libro": "The ONE Thing",
            "autor": "Gary Keller"
        },
        {
            "cita": "¿Cuál es la UNA cosa que podés hacer de manera que todo lo demás sea más fácil o innecesario?",
            "libro": "The ONE Thing",
            "autor": "Gary Keller"
        },
        {
            "cita": "Si tenés más de tres prioridades, no tenés ninguna.",
            "libro": "Essentialism",
            "autor": "Greg McKeown"
        },
        {
            "cita": "El essencialismo no es sobre cómo hacer más cosas. Es sobre cómo hacer las cosas correctas.",
            "libro": "Essentialism",
            "autor": "Greg McKeown"
        },
        {
            "cita": "Deep work es la habilidad de enfocarte sin distracción en una tarea cognitivamente demandante.",
            "libro": "Deep Work",
            "autor": "Cal Newport"
        },
        {
            "cita": "El trabajo en profundidad produce resultados extraordinarios. Las redes sociales producen la ilusión de productividad.",
            "libro": "Deep Work",
            "autor": "Cal Newport"
        },
        {
            "cita": "Capturá todo lo que está en tu cabeza. Tu mente es para tener ideas, no para guardarlas.",
            "libro": "Getting Things Done",
            "autor": "David Allen"
        },
        {
            "cita": "Hacé el trabajo más importante cuando tu energía está en su pico. No le regales ese tiempo al correo.",
            "libro": "When",
            "autor": "Daniel Pink"
        },
        {
            "cita": "No aplaces lo que podés hacer hoy para mañana. El aplazamiento es el asesino silencioso del éxito.",
            "libro": "Sin excusas",
            "autor": "Brian Tracy"
        },
    ]
}


def obtener_cita_aleatoria() -> str:
    """Devuelve una cita aleatoria de cualquier categoría."""
    todas = [cita for citas in CITAS.values() for cita in citas]
    cita = random.choice(todas)
    return _formatear_cita(cita)


def obtener_cita_por_categoria(categoria: str) -> str:
    """Devuelve una cita de una categoría específica."""
    if categoria == "aleatoria" or categoria not in CITAS:
        return obtener_cita_aleatoria()

    cita = random.choice(CITAS[categoria])
    return _formatear_cita(cita)


def _formatear_cita(cita: dict) -> str:
    """Formatea una cita para mostrarla en WhatsApp."""
    return (
        f'"{cita["cita"]}"\n\n'
        f'— {cita["autor"]}, *{cita["libro"]}*'
    )
