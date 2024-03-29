# DEPRECATED: PLEASE USE THE CURL SCRIPT OR QUERY THE ELASTICSEARCH

# Pathfinder 2e item scrape
> Tags: Pathfinder 2e pf2 item equipment
>
Script to scrape pathfinder 2nd edition items from https://2e.aonprd.com/ and save them in csv. 

CSV data structure:

| ID  |   Title   |    Level   |   Rarity    |      Price       |   Traits    |      Link       |
|:---:|:---------:|:----------:|:-----------:|:----------------:|:-----------:|:---------------:|
| ID  | Item name | Item level | Item rarity | Item price in GP | Item traits | Link to pf2 prd |


This tool uses trademarks and/or copyrights owned by Paizo Inc., used under Paizo's Community Use Policy ([paizo.com/communityuse](https://paizo.com/community/communityuse)). We are expressly prohibited from charging you to use or access this content. This tool is not published, endorsed, or specifically approved by Paizo. For more information about Paizo Inc. and Paizo products, visit paizo.com.

## Installing / Getting started

To use this script you need `python-3.x` and downloaded csv from [2e.aonprd.com/Equipment.aspx?All=true](https://2e.aonprd.com/Equipment.aspx?All=true) You can find how to do it in [here](./README.md#how-to-download-input-csv). Then you need to install
requirements from req.txt and you are good to go.

```shell
pip install -r req.txt
py pf2eq_scrape.py [-h] fileName
```

Scraped items will be saved into the `input.csv` file located in the script folder.

## How to download input csv

To download input CSV go to [2e.aonprd.com/Equipment.aspx?All=true](https://2e.aonprd.com/Equipment.aspx?All=true) and go to bottom of the page. There change `Page size` to number greater or equal to number of all items (at time of writing it's > 2717) and hit `Change` button. After page reloads click the small page icon with csv written on it on either right bottom or right top of the table.

After downloading please check the file for some minor corruptions which can happen. Useful regular expression is `\r\n^[^"]` which will catch all lines separated after item name.

## Licensing

The code in this project is licensed under GNU GENERAL PUBLIC LICENSE license.

<!--

### Initial Configuration

Some projects require initial configuration (e.g. access tokens or keys, `npm i`).
This is the section where you would document those requirements.

## Developing

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/your/awesome-project.git
cd awesome-project/
packagemanager install
```

And state what happens step-by-step.

### Building

If your project needs some additional steps for the developer to build the
project after some code changes, state them here:

```shell
./configure
make
make install
```

Here again you should state what actually happens when the code above gets
executed.

### Deploying / Publishing

In case there's some step you have to take that publishes this project to a
server, this is the right time to state it.

```shell
packagemanager deploy awesome-project -s server.com -u username -p password
```

And again you'd need to tell what the previous code actually does.

## Features

What's all the bells and whistles this project can perform?
* What's the main functionality
* You can also do another thing
* If you get really randy, you can even do this

## Configuration

Here you should write what are all of the configurations a user can enter when
using the project.

#### Argument 1
Type: `String`  
Default: `'default value'`

State what an argument does and how you can use it. If needed, you can provide
an example below.

Example:
```bash
awesome-project "Some other value"  # Prints "You're nailing this readme!"
```

#### Argument 2
Type: `Number|Boolean`  
Default: 100

Copy-paste as many of these as you need.

## Contributing

When you publish something open source, one of the greatest motivations is that
anyone can just jump in and start contributing to your project.

These paragraphs are meant to welcome those kind souls to feel that they are
needed. You should state something like:

"If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome."

If there's anything else the developer needs to know (e.g. the code style
guide), you should link it here. If there's a lot of things to take into
consideration, it is common to separate this section to its own file called
`CONTRIBUTING.md` (or similar). If so, you should say that it exists here.

## Links

Even though this information can be found inside the project on machine-readable
format like in a .json file, it's good to include a summary of most useful
links to humans using your project. You can include links like:

- Project homepage: https://your.github.com/awesome-project/
- Repository: https://github.com/your/awesome-project/
- Issue tracker: https://github.com/your/awesome-project/issues
  - In case of sensitive bugs like security vulnerabilities, please contact
    my@email.com directly instead of using issue tracker. We value your effort
    to improve the security and privacy of this project!
- Related projects:
  - Your other project: https://github.com/your/other-project/
  - Someone else's project: https://github.com/someones/awesome-project/

-->