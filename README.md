# MyRayTracer

## Overview 

This is a python implementation of the famous **Ray Tracing in One Weekend** and **Ray Tracing: The next week. It was a project for Graphic computation subject in my university. I can't see any use of it, since python is extremaly slow but it may help you if your teacher asks to implement a renderer in python.

## Portugues What was the delivered:

##### Aluno: João Marcos Mororo Costa

## Visão Geral

Essa é uma implementação em python do **Ray Tracing in One Weekend**, encontrado em https://github.com/petershirley/raytracinginoneweekend de Peter Shiley. Feito para o tp2 de Computação Gráfica.

## Instruções

### Parâmetros/Argumentos

Existem 5 possíveis argumentos, os quais todos são opcionais:

1. --resolution ou -r que recebe duas integrais x e y que vão definir a definição da imagem a ser renderizada. 
    default - 340 480
2. -spp é a quantidade de raios gerados por pixel (samples per pixel). 
    default - 64
3. -scene defini a cena que será renderizada. Existem 4 possíveis cenas: 
    * basic  - Cena simples para testes e rápidas renderizações.
    * random - Cena contida na capa do livro do Perer Shirley.
    * motion - Demonstra a funcionalidade de montion blur.
    * cube   - Renderiza dois cubos um difuso e outro metálico.
default - basic
4. --image ou -i endereço relativo da imagem final.
    default - results/image.ppm
5. --threads ou -t numero de processos usados pelo programa.
    default - Numero de cores contidos na sua cpu.

## Implementação:

A implementação é praticamente uma tradução do livro **Ray Tracing in One Weekend** de C para Python. As funcionalidades extras 1 e 4, pedidas no tp, foram implementadas usando 0 livro **Ray Tracing: The Next Week** sequencia do livro anterior. Nesse documento tentarei focar nas diferenças entre as implementações contidas no programa e a dos livros.

### Multi Threading

Python é uma linguagem lenta quando comparada com linguagens de baixo nível com c, c++ ou rust, o que torna python uma pessima escolha para implementação de um renderer. Uma linguagem lenta torna processo de desenvolvimento se torna mais lento e penoso, a mais simples imagem demora décadas para renderizar. Uma forma de amenizar o problema da velocidade é utilizar da programação paralela.

Foi utilizado uma multiprocessing, com a biblioteca **multiprocessing**, abordagem para acelerar o programa. A principal motivo de utilizar multiprocessing ao invex de multithreading foi por causa do **THE GLOBAL INTERPRETER LOCK** do python que faz com que o multi threading do python funcione em apenas um core, o que definitivamente não resolve o problema de velocidade do renderer.

Para tornar a implementação simples o programa foi divido em linhas sendo a renderização de cada linha um trabalho a ser executado por um dos processos. Essa abordagem é bem favorável por ser bem compativel com a classe Pool que deixa o programa pequeno e limpo. Basicamente foi necessário apenas duas linhas para termos isso funcionando:

```python
pool = multiprocessing.Pool(processes = args.threads)
results = pool.imap(partial(doWork, cam = cam, world = world, spp = args.spp, NX = args.resolution[0], NY args.resolution[1]), reversed(range(0, args.resolution[1])))
```
Perceba que foi usado imap ao invez de map. A razão disso é que o imap permite interação em tempo real com resultados de tarefas finalizadas. Isso permitiu acompanhar o progresso da renderização assim como prever o tempo restante para finaliza-lá. Apesar da previsão do tempo restante ser bastante impressiva devido ao fato de algumas linhas serem muito mais baratas que outras.

### Diferentes superfices:

Além das esferas, também foi implementado quadrados como uma superfície alternativa. Eles foram utilizados para renderização dos cubos e do plano da imagem cube.ppm. Foi utilizada a implementação contida no **Ray Tracing: The Next Week** que define três superfícies xy_rec, xz_rec, yz_rec o que torna extremamente fácil a implementação e a utilização para criação de cubos por exemplos. Porém tal abordagem é bastante limitada, sendo inútil para meshes mais complicadas. Além disso, essa abordagem leva a repetição de código e outras problemas. Apesar disso, a abordagem é muito simples e muito compatível com todo o resto do código.
 ```python 
 class xy_rect:

    def __init__(self, material, x0, x1, y0, y1, k):
        self.material = material
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.k = k
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k - r.getOrigin()[2]) / r.getDirection()[2]
        if t < t_min or t > t_max:
            return False
        x = r.getOrigin()[0] + t * r.getDirection()[0]
        y = r.getOrigin()[1] + t * r.getDirection()[1]
        if x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1:
            return False
        rec.t = t
        rec.point = r.pointAt(rec.t)
        rec.normal = vec3(0, 0, 1)
        rec.material = self.material
        return True
```

### Motion Blur

A implementação de motion blur também foi retirada do **Ray Tracing: The Next Week**.

Motion Blur é um efeito bastante observado em fotografias e acontece porque os raios de luz registrados pela camera não chegam todos no mesmo momento, mas em um certo intervalo de tempo. Portanto, para gerar o mesmo efeito no nosso renderer precisamos gerar os raios de luz em diferentes momentos. Para isso foi adicionado uma variable self.__time ao ray e foi modificado o código da função getRay da câmera para levar em consideração o tempo.

```python
    def getRay(self, u, v):
        rd = randomInUnitDisk() * self.__lens_radius
        offset = u * rd[0] + v * rd[1]
        position = vec3(self.__position[0] + offset, self.__position[1] + offset, self.__position[2] + offset)
        time = self.__time0 + random.uniform(0, 1) * (self.__time0 - self.__time1)
        return ray(position, self.__lower_left + self.__horizontal*u + self.__vertical*v - position, time)
```

Como pode ver o rio é gerado em um momento aleatório entre um pré determinado intervalo de tempo.

## Referencia:

* https://github.com/petershirley
* https://github.com/petershirley/raytracingthenextweek
* https://github.com/appleseedhq/appleseed
* http://jessenoller.com/blog/2009/02/01/python-threads-and-the-global-interpreter-lock/
