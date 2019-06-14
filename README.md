# MyRayTracer

## Visão Geral

Essa é uma implementação em python do Ray Tracing in One Weekend encontrado em https://github.com/petershirley/raytracinginoneweekend de Peter SHiley.

## Instruções

### Parametros

Existem 5 possiveis argumentos, os quais todos são opicionais:

1. --resolution ou -r que recebe duas integrais x e y que vão definir a definição da imagem a ser redenrizada. 
    default - 340 480
2. -spp é a quantidade de raios gerados por pixel (samples per pixel). 
    default - 64
3. -scene defini a cena que será renderizada. Existem 4 possiveis cenas: 
    1. basic  - Cena simples para testes e rapidas renderizações.
    2. random - Cena contida na capa do livro do Perer Shirley.
    3. motion - Demonstra a funcionalidade de montion blur.
    4. cube   - Renderiza dois cubos um difuso e outro metalico.
default - basic
4. --image ou -i endereço relativo da imagem final.
    default - results/image.ppm
5. --threads ou -t numero de processos usados pelo programa.
    default - Numero de cores contidos na sua cpu.

## Implementação:

A implementação é praticamente uma tradução do livro Ray Tracing in One Weekend para python sendo que para as funcionalidades extras 1 e 4 foram usados a sequencia desse livro Ray Tracing: The Next Week. Nesse documento tentarei focar nas diferenças entre as implmentações.

### Multi Threading

Python é uma lingugem muito lenta quando comparada com linguagens de baixo nível com c, c++ ou rust. O que torna uma pessima escolha para implementação de um renderer. O processo de desenvolvimento se torna mais lento e penoso, e as mais simples imagens demoram décadas para renderizar. Uma forma de amenizar o problema é utilizar da programação paralela.

Não é correto falar que foi usado multi Threading no programa, pois na realidade é utilizada uma abordadem multi processing. Que possuem algumas diferenças como por exemplo multi processing não compartilha informação e entre o outros. A principal razação de utilizar multi processing é porcausa de uma caracteristica do python chamada xxx que faz com que o multi threading do python funcione em apenas um core, o que definitivamente não resolve o problema de eficiencia do programa. Para contornar esse problema foi utilizada a biblioteca multiprocessing que cria novos processos ao invez de novos threads.

Para tornar a implementação simples o programa foi divido em linhas sendo a renderização de cada linha um trabalho a ser executado por um dos processo. Essa abordagem é bem favoravel por ser bem compativel com a classe Pool que deixa o programa pequeno e limpo. Basicamente foi necessario apenas duas linhas:

```python
pool = multiprocessing.Pool(processes = args.threads)
results = pool.imap(partial(doWork, cam = cam, world = world, spp = args.spp, NX = args.resolution[0], NY args.resolution[1]), reversed(range(0, args.resolution[1])))
```
Perceba que foi usado imap ao invez de map. A razão disso é que o imap permite interação em tempo real com resultados de tarefas finalizadas. Isso permitiu acompanhar o progresso da renderização assim como prever o tempo restante para finaliza-lá. Apesar da previsão do tempo restante ser bastante impressiva devido ao fato de algumas linhas serem muito mais baratas que outras.
