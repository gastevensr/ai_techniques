/*var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");
ctx.beginPath();
ctx.arc(95, 50, 40, 0, 2*Math.PI);
ctx.stroke();
*/

class Genome {
    constructor(numBits) {
        this.fitness = 0.0;
        if (numBits == 0) {
            this.bits = [];
        } else {
            this.bits = Array.from({length: numBits}, () => Math.floor(Math.random() * (1 + 1)));
        }
    }
}
///////////////////////////////////////////////

class GameMap {
    constructor(matrix, entrance, exit, rows, columns) {
        this.map = matrix
        this.entrance = entrance;
		this.exit = exit;
		this.mapHeight = rows;
        this.mapWidth  = columns;
        this.findEntranceExitCoords();
		this.resetMemory();
    }

    findEntranceExitCoords() {
		for (let y = 0; y < this.mapHeight; y++) {
			for (let x = 0; x < this.mapWidth; x++) {
				if (this.map[y][x] == this.entrance) {
					this.startX = x;
					this.startY = y;
				} else if (this.map[y][x] == this.exit) {
					this.endX = x;
					this.endY = y;
				}
			}
		}
    }

    /**
	 * Resets the memory map to zeros.
	 */
    resetMemory() {
        this.memory = [...Array(this.mapHeight)].map(e => Array(this.mapWidth).fill(0));
        this.direction = [...Array(this.mapHeight)].map(e => Array(this.mapWidth).fill(0));
	}

    /**
	 * Takes a string of directions and see's how far Bob can get. Returns a
	 * fitness score proportional to the distance reached from the exit.
	 * 
	 * @param path
	 * @param memory
	 * @return
	 */
	testRoute(path, memory) {
		let posX = this.startX;
        let posY = this.startY;

		for (let dir = 0; dir < path.length; dir++) {
			const nextDir = path[dir];
			switch (nextDir) {
            case 0: // North
				// Check within bounds and that we can move.
				if (posY - 1 >= 0 && this.map[posY - 1][posX] != 1) {
					posY--;
				}
				break;
            case 1: // South
				// Check within bounds and that we can move.
				if (posY + 1 < this.mapHeight && this.map[posY + 1][posX] != 1) {
					posY++;
				}
				break;
            case 2: // East
				// Check within bounds and that we can move.
				if (posX + 1 < this.mapWidth && this.map[posY][posX + 1] != 1) {
					posX++;
				}
				break;
            case 3: // West
				// Check within bounds and that we can move.
				if (posX - 1 >= 0 && this.map[posY][posX - 1] != 1) {
					posX--;
				}
				break;
			}// end switch
            // mark the route and direction in the memory array
            memory[posY][posX] = 1 + (10 * (nextDir + 1));
		} // next direction
		// Now we know the finish point of Bob's journey, let's assign
		// a fitness score which is proportional to his distance from
		// the exit.
		const diffX = Math.abs(posX - this.endX);
		const diffY = Math.abs(posY - this.endY);

		// We add the one to ensure we never divide by zero. Therefore
		// a solution has been found when this return value = 1
    	return 1.0 / (diffX + diffY + 1.0);
    }

    setMemory(array) {// TODO optimize this
		for (let i = 0; i < array.length; i++) {
			for (let j = 0; j < array[0].length; j++) {
                this.memory[i][j] = array[i][j];
                //this.memory[i][j].direction = array[i][j].direction;
			}
		}
    }

    /**
	 * Given a surface to draw on this function uses the windows GDI to display
	 * the map.
	 * @param width
	 * @param height
	 * @param canvas
	 */
	render(width, height, canvas) {
		canvas.fillStyle = "#FFF";
		canvas.clearRect(0, 0, width, height);
		let border = 20;

		const blockSizeX = (width - 2 * border) / this.mapWidth;
		const blockSizeY = (height - 2 * border) / this.mapHeight;

		canvas.fillStyle = "#000";
		for (let y = 0; y < this.mapHeight; y++) {
			for (let x = 0; x < this.mapWidth; x++) {
                
				// Calculate the corners of each cell.
				const left = border + (blockSizeX * x);
				const top = border + (blockSizeY * y);
				// Draw a black rectangle if this is a wall.
				if (this.map[y][x] == 1) {
                    //console.log([left, top, blockSizeX, blockSizeY])
                    canvas.fillRect(left, top, blockSizeX, blockSizeY);
				}
			}
		}
    }
    
    /**
	 * Draws whatever path may be stored in the memory.
	 * @param width
	 * @param height
	 * @param canvas
	 */
	memoryRender(width, height, canvas) {
		const border = 20;
		const blockSizeX = (width - 2 * border) / this.mapWidth;
        const blockSizeY = (height - 2 * border) / this.mapHeight;
        canvas.fillStyle = "#00F";
        canvas.strokeStyle = "#FF0";
		for (let y = 0; y < this.mapHeight; y++) {
			for (let x = 0; x < this.mapWidth; x++) {
                let dir = 0;
                let val = 0;
                if (this.memory[y][x] > 0) {
                    dir = ((this.memory[y][x] - 1) / 10) - 1;
                    val = 1;
                } else {
                    continue;
                }
				// Calculate the corners of each cell.
				const left = border + (blockSizeX * x);
				const top = border + (blockSizeY * y);
                // Draw a blue path.
                
				if (val == 1) {
                    canvas.fillRect(left, top, blockSizeY, blockSizeY);
                    
                    canvas.beginPath();
					switch (dir) {
					case 0:// North
                        canvas.moveTo(left + blockSizeX / 2, top);
                        canvas.lineTo(left + blockSizeX, top + blockSizeY);
                        canvas.lineTo(left, top + blockSizeY);
						break;
					case 1://South
                        canvas.moveTo(left + blockSizeX / 2, top + blockSizeY);
                        canvas.lineTo(left + blockSizeX, top);
                        canvas.lineTo(left, top);
						break;
					case 2:// East
                        canvas.moveTo(left + blockSizeX, top + blockSizeY / 2);
                        canvas.lineTo(left, top + blockSizeY);
                        canvas.lineTo(left, top);
						break;
					case 3:// West
                        canvas.moveTo(left, top + blockSizeY / 2);
                        canvas.lineTo(left + blockSizeX, top + blockSizeY);
                        canvas.lineTo(left + blockSizeX, top);
						break;
                    }
                    canvas.closePath();
                    canvas.stroke();
				}
			}
		}
    }

    drawGates(width, height, canvas) {
		const border = 20;

		const blockSizeX = (width - 2 * border) / this.mapWidth;
		const blockSizeY = (height - 2 * border) / this.mapHeight;

		let left = border + (blockSizeX * this.startX);
		let top = border + (blockSizeY * this.startY);
		// Entrance is green.
        canvas.fillStyle = "#0F0";
		canvas.fillRect(left, top, blockSizeX, blockSizeY);

		left = border + (blockSizeX * this.endX);
        top = border + (blockSizeY * this.endY);
        // Exit is red.
		canvas.fillStyle = "#F00";
		canvas.fillRect(left, top, blockSizeX, blockSizeY);
	}
}
///////////////////////////////////////////////

class Bob {
    constructor(crossoverRate,
        mutationRate,
        populationSize,
        chromosomeLength,
        geneLength,
        entrance,
        exit,
        matrix,
        rows,
        columns,
        canvas) {
        this.crossoverRate = crossoverRate;
        this.mutationRate = mutationRate;
        this.populationSize = populationSize;
        this.chromosomeLength = chromosomeLength;
        this.geneLength = geneLength;
        this.entrance = entrance;
        this.exit = exit;
        this.matrix = matrix;
        this.rows = rows;
        this.columns = columns;
        this.canvas = canvas;
        this.canvas.font = "14px Georgia";

        this.START = "Press Return to start a new run";
        this.STOP = "Press Space to stop";
        this.genomes = [];
		this.bobMap = new GameMap(matrix, entrance, exit, rows, columns);
		this.bobBrain = new GameMap(matrix, entrance, exit, rows, columns);
		this.totalFitnessScore = 0.0;
		this.generation = 0;
        this.busy = false;
    }

    /**
	 * Iterates through each genome flipping the bits according to the mutation rate.
	 * @param bits
	 */
    mutate(bits) {
        //console.log('befor: ' + bits);
		for (let currBit = 0; currBit < bits.length; currBit++) {
			// do we flip this bit?
			if (Math.random() < this.mutationRate) {
				// flip the bit
				bits[currBit] = 1 - bits[currBit];
			}
        } // next bit
        //console.log('after: ' + bits);
        return bits;
    }

    /**
	 * Takes 2 parent vectors, selects a midpoint and then swaps the ends of
	 * each genome creating 2 new genomes which are stored in baby1 and baby2.
	 * 
	 * @param mom
	 * @param dad
	 * @param baby1
	 * @param baby2
	 */
	crossover(mom, dad, baby1, baby2) {
		// Just return parents as offspring dependent on the rate or if
		// parents are the same.
		if (Math.random() > this.crossoverRate || mom.bits === dad.bits) {
			baby1.bits = mom.bits;
            baby2.bits = dad.bits;
            //console.log('returning from if');
			return;
		}

		// Determine a crossover point.
        const cp = this.randomInt(this.chromosomeLength);// TODO check range

        // Swap the bits.
        let x = 0;
		for (let i = 0; i < cp; i++) {
			baby1.bits.push(mom.bits[i]);
            baby2.bits.push(dad.bits[i]);
            x++;
        }

		for (let i = cp; i < mom.bits.length; i++) {
			baby1.bits.push(dad.bits[i]);
            baby2.bits.push(mom.bits[i]);
            x++;
        }
    }

    randomInt(max) {
        return Math.floor(Math.random() * Math.floor(max));
    }

	/**
	 * Selects a member of the population by using roulette wheel selection as
	 * described in the text.
	 * 
	 * @return the selected genome.
	 */
	rouletteWheelSelection() {
		const slice = Math.random() * this.totalFitnessScore;
		let cfTotal = 0.0;
		let selectedGenome = 0;
		for (let i = 0; i < this.populationSize; i++) {
			const genome = this.genomes[i];
			cfTotal += genome.fitness;
			if (cfTotal > slice) {
				selectedGenome = i;
				break;
			}
        }
		return selectedGenome;
	}

    /**
	 * Updates the genomes fitness with the new fitness scores and calculates
	 * the highest fitness and the fittest member of the population. Also sets
	 * m_pFittestGenome to point to the fittest. If a solution has been found
	 * (fitness == 1 in this example) then the run is halted by setting m_bBusy
	 * to false.
	 */
	updateFitnessScores() {
		this.fittestGenome = 0;
		this.bestFitnessScore = 0;
		this.totalFitnessScore = 0;

		const tempMemory = new GameMap(this.matrix, this.entrance, this.exit, this.rows, this.columns);
		// Update the fitness scores and keep a check on fittest so far.
		for (let i = 0; i < this.populationSize; i++) {
			// Decode each genomes chromosome into a vector of directions.
			const directions = this.decode(this.genomes[i].bits);
			// Get its fitness score.
			this.genomes[i].fitness = this.bobMap.testRoute(directions, tempMemory.memory);
			// Update total.
			this.totalFitnessScore += this.genomes[i].fitness;
			// If this is the fittest genome found so far, store results.
			if (this.genomes[i].fitness > this.bestFitnessScore) {
				this.bestFitnessScore = this.genomes[i].fitness;
				this.fittestGenome = i;
				this.bobBrain.setMemory(tempMemory.memory);
                // Has Bob found the exit?
                //console.log('fitness: ' + (this.genomes[i].fitness - 1.0));
				if (this.genomes[i].fitness == 1.0) {
					// If so, stop the run.
                    this.busy = false;
				}
			}
			tempMemory.resetMemory();
		} // next genome
    }

    /**
	 * Decodes a vector of bits into a vector of directions (ints).
	 * North = 0, South = 1, East = 2, West = 3
	 * 
	 * @param bits
	 * @return
	 */
	decode(bits) {
		const directions = [];
		// Step through the chromosome a gene at a time.
		for (let gene = 0; gene < bits.length; gene += this.geneLength) {
			// Get the gene at this position.
			const thisGene = [];
			for (let bit = 0; bit < this.geneLength; bit++) {
				thisGene.push(bits[gene + bit]);
			}
			// Convert to decimal and add to list of directions.
			directions.push(this.binToInt(thisGene));
		}
		return directions;
    }

    /**
	 * Converts a vector of bits into decimal. Used by <code>decode.</code>
	 * 
	 * @param vector
	 * @return
	 */
	binToInt(list) {
		let val = 0;
		let multiplier = 1;

		for (let bit = list.length; bit > 0; bit--) {
			val += list[bit - 1] * multiplier;
			multiplier *= 2;
		}
		return val;
    }

    /**
	 * Creates an initial population of random bit strings.
	 */
	createInitialPopulation() {
		// Clear existing population.
        this.genomes = [];
		for (let i = 0; i < this.populationSize; i++) {
			this.genomes.push(new Genome(this.chromosomeLength));
        }

		// Reset all variables.
		this.generation = 0;
		this.fittestGenome = 0;
		this.bestFitnessScore = 0;
		this.totalFitnessScore = 0;
    }

    /**
	 * This is the function that starts everything. It is mainly another windows
	 * message pump using PeekMessage instead of GetMessage so we can easily and
	 * dynamically make updates to the window while the GA is running.
	 * Basically, if there is no msg to be processed another Epoch is performed.
	 */
	run() {
		// The first thing we have to do is create a random population of genomes.
		this.createInitialPopulation();
		this.busy = true;
    }

    /**
	 * Given a surface to render to this function renders the map and the best path if relevant. mapWidth/mapHeight
	 * are the dimensions of the client window.
	 * @param mapWidth
	 * @param mapHeight
	 */
	render(mapWidth, mapHeight) {
        this.canvas.clearRect(0, 0, mapWidth, mapHeight);
		// Render the map.
		this.bobMap.render(mapWidth, mapHeight, this.canvas);
		// Render the best route.
		this.bobBrain.memoryRender(mapWidth, mapHeight, this.canvas);
        // Render additional information.
        this.canvas.fillStyle = "#000";
		this.canvas.fillText("Generation: " + (this.generation), 5, 15);// generation minus 1?
		if (!this.busy) {
			this.canvas.fillText(this.START, mapWidth / 2 - (this.START.length * 3), mapHeight - 5);
			this.bobMap.drawGates(mapWidth, mapHeight, this.canvas);
		} else {
			this.canvas.fillText(this.STOP, mapWidth / 2 - (this.START.length * 3), mapHeight - 5);
		}
    }

    /**
	 * This is the workhorse of the GA. It first updates the fitness scores of
	 * the population then creates a new population of genomes using the
	 * selection, croosover and mutation operators we have discussed.
	 */
	epoch() {
		this.updateFitnessScores();
		// Now to create a new population.
		let newBabies = 0;

		// Create some storage for the baby genomes.
		let babyGenomes = [];

		while (newBabies < this.populationSize) {
			// Select 2 parents.
			let mom = this.genomes[this.rouletteWheelSelection()];
            let dad = this.genomes[this.rouletteWheelSelection()];

			// Operator: crossover
			let baby1 = new Genome();
			let baby2 = new Genome();
			this.crossover(mom, dad, baby1, baby2);

			// Operator: mutate
			baby1.bits = this.mutate(baby1.bits);
			baby2.bits = this.mutate(baby2.bits);

			// Add to new population.
			babyGenomes.push(baby1);
			babyGenomes.push(baby2);

			newBabies += 2;
		}
		// Copy babies back into starter population.
		this.genomes = babyGenomes;

		// Increment the generation counter.
        this.generation++;
	}
}

let data = '{\
	"crossoverRate": 0.7,\
	"mutationRate": 0.001,\
	"populationSize": 140,\
	"chromosomeLength": 70,\
	"geneLength": 2,\
	"entrance": 2,\
	"exit": 3,\
	"rows": 10,\
	"columns": 15,\
	"gameMap": [\
		"111111111111111",\
		"101000001110001",\
		"200000001110001",\
		"100011100100001",\
		"100001000000101",\
		"110011100000001",\
		"100001000011101",\
		"101100010000003",\
		"101100010000001",\
		"111111111111111"\
	]\
}\
';
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext("2d");
let json = JSON.parse(data);
const bob = new Bob(
    json['crossoverRate'],
    json['mutationRate'],
    json['populationSize'],
    json['chromosomeLength'],
    json['geneLength'],
    json['entrance'],
    json['exit'],
    json['gameMap'],
    json['rows'],
    json['columns'],
    ctx
);

bob.render(canvas.width, canvas.height);

function start() {
    bob.run();

    var x = 0;
    while (bob.busy) {
        bob.epoch();
        bob.render(canvas.width, canvas.height);
        x++;
        if (x > 1000) {
            console.log('break');
            break;
        }
    }
}
