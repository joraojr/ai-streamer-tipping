class Model {
    /** hold all current game state */
    constructor() {
        this.progress = {};
        this.sliders = {};
    }

    reset() {
        this.progress = {};
        this.sliders = {};
    }

    load(sliders) {
        this.sliders = sliders;
        for (let s in this.sliders) this.sliders[s].attempts = 0;
    }
}


class View {
    /** renders everything */
    constructor(model, size) {
        this.model = model;
        this.slider_size = size;
        this.$progress = document.getElementById("progress-bar");
        this.$canvas = document.getElementById("canvas");
        this.size = [];
        this.grid = [];
        this.img = new Image();
        this.canvas = this.$canvas.getContext('2d');
        this.picked_slider = null;
    }

    reset() {
        this.img.src = "";
        this.size = [];
        this.grid = [];
    }

    clear() {
        this.canvas.clearRect(0, 0, this.$canvas.wodth, this.$canvas.height);
    }

    load(size, image, grid) {
        this.size = size;
        this.grid = grid;
        this.img.src = image;
        this.img.width = size[0];
        this.img.height = size[1];
        this.$canvas.width = this.img.width;
        this.$canvas.height = this.img.height;
    }

    render() {
        if (this.img.src && !this.img.complete) {  // image's still loading
            this.img.onload = () => this.render();
            return;
        }
        this.canvas.drawImage(this.img, 0, 0);
        this.grid.forEach((coord, i) => {
            let slider = this.model.sliders[i]
            let x = coord[0] + slider.value,
                y = coord[1];
            this.drawHandle(x, y, {correct: slider.is_correct});
        });
    }

    drawSlider(i, state) {
        let x0 = this.grid[i][0], y0 = this.grid[i][1];
        let w = this.slider_size[0] + 40, h = this.slider_size[1];  // +40 margin
        let sx = x0 - w / 2, sy = y0 - h / 2;
        // copy slider cell from vackground image
        this.canvas.drawImage(this.img, sx, sy, w, h, sx, sy, w, h);
        // draw handle
        let slider = this.model.sliders[i];
        let x = x0 + slider.value;
        state.correct = slider.is_correct;
        this.drawHandle(x, y0, state);
    }

    drawHandle(x, y, state) {
        // hover area
        if (state.hover) {
            this.canvas.fillStyle = "rgba(98, 0, 238, 0.04)";
            this.canvas.beginPath();
            this.canvas.arc(x, y, 20, 0, 2 * Math.PI);
            this.canvas.fill();
        } else if (state.dragged) {
            this.canvas.fillStyle = "rgba(98, 0, 238, 0.24)";
            this.canvas.beginPath();
            this.canvas.arc(x, y, 20, 0, 2 * Math.PI);
            this.canvas.fill();
        }

        // knob
        if (state.correct) {
            this.canvas.fillStyle = "rgb(0, 199, 0)";
        } else if (state.dragged) {
            this.canvas.fillStyle = "rgba(13, 110, 253, 0.5)";
        } else {
            this.canvas.fillStyle = "rgb(13, 110, 253)";
        }
        this.canvas.beginPath();
        this.canvas.arc(x, y, 10, 0, 2 * Math.PI);
        this.canvas.fill();
    }

    pickHandle(x, y) {
        for (let i = 0; i < this.grid.length; i++) {
            let slider = this.model.sliders[i];
            let x0 = this.grid[i][0] + slider.value, y0 = this.grid[i][1];
            let dx = x - x0, dy = y - y0;
            if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
                if (slider.attempts < js_vars.params.attempts_per_slider) return i;
                return null;
            }
        }
        return null;
    }

    mapHandle(i, x, y) {
        // return a value corresponding to coords
        let dx = x - this.grid[i][0];
        return Math.abs(dx) < this.slider_size[0] / 2 ? dx : null;
    }

    renderProgress() {
        this.$progress.value = this.model.progress.solved;
    }
}

class Controller {
    /** handles everything */
    constructor(model, view) {
        this.model = model;
        this.view = view;

        this.starting = true;
        this.ts_question = 0;
        this.ts_answer = 0;
        this.input_disabled = false;

        window.liveRecv = (message) => this.recvMessage(message);

        this.picked_slider = null;
        this.hover_handle = null;
        this.view.$canvas.onmousedown = (e) => this.pickHandle(e);
        this.view.$canvas.onmousemove = (e) => this.picked_slider !== null ? this.dragHandle(e) : this.hoverHandle(e);
        this.view.$canvas.onmouseup = (e) => this.picked_slider !== null ? this.dropHandle(e) : null;

        liveSend({type: 'load'});
    }

    recvMessage(message) {
        // console.debug("received:", message);
        switch (message.type) {
            case 'status':
                if (message.puzzle) {  // restoring existing state
                    this.starting = false;
                    this.recvPuzzle(message.puzzle);
                } else if (message.progress.iteration === 0) {   // start of the game
                    this.startGame();
                } else if (message.iterations_left === 0) {  // exhausted max iterations
                    this.endGame();
                }
                break;

            case 'puzzle':
                this.recvPuzzle(message.puzzle);
                break;

            case 'feedback':
                this.recvFeedback(message);
                break;

            case 'solution':
                this.cheat(message.solution);
                break;
        }

        if ('progress' in message) { // can be added to message of any type
            this.recvProgress(message.progress);
        }
    }

    recvPuzzle(data) {
        this.model.load(data.sliders);
        this.view.load(data.size, data.image, data.grid);
        this.view.render();
    }

    recvFeedback(message) {
        let i = message.slider;
        this.model.sliders[i].value = message.value;
        this.model.sliders[i].is_correct = message.is_correct;
        this.view.render();

        if (message.is_completed) {
            window.setTimeout(() => this.endGame(), js_vars.params.trial_delay * 1000);
        }
    }

    recvProgress(data) {
        this.model.progress = data;
        this.view.renderProgress();
    }

    startGame() {
        this.starting = false;
        this.reqNew();
    }

    // TODO create function that submit slider in parallel
    submitSlider(i) {
        let slider = this.model.sliders[i];
        slider.attempts++;
        slider.is_correct = null;
        liveSend({type: 'value', slider: i, value: slider.value});
    }

    reqNew() {
        this.model.reset();
        this.view.reset();
        this.view.clear();

        liveSend({type: 'new'});
    }

    pickHandle(event) {
        if (this.input_disabled || $("#player_role").val() === "viewer" || ["BOT_NO_PAY_HUMAN", "BOT_PAYS_HUMAN", "BOT_NO_PAY_BOT", "BOT_PAYS_BOT"].includes(js_vars.params.treatment)) return;

        let i = this.view.pickHandle(event.offsetX, event.offsetY);
        this.picked_slider = i;
        if (i !== null) {
            this.view.drawSlider(i, {dragged: true});
        }
    }

    hoverHandle(event) {
        let i = this.view.pickHandle(event.offsetX, event.offsetY);
        if ($("#player_role").val() === "viewer" || ["BOT_NO_PAY_HUMAN", "BOT_PAYS_HUMAN", "BOT_NO_PAY_BOT", "BOT_PAYS_BOT"].includes(js_vars.params.treatment)) return;
        if (this.hover_handle !== i) {
            if (this.hover_handle !== null) {
                this.view.drawSlider(this.hover_handle, {hover: false});
            }
            this.hover_handle = i;
            if (this.hover_handle !== null) {
                this.view.drawSlider(this.hover_handle, {hover: true});
            }
        }
    }

    dragHandle(event) {
        let i = this.picked_slider;
        let val = this.view.mapHandle(i, event.offsetX, event.offsetY);
        if ($("#player_role").val() === "viewer" || ["BOT_NO_PAY_HUMAN", "BOT_PAYS_HUMAN", "BOT_NO_PAY_BOT", "BOT_PAYS_BOT"].includes(js_vars.params.treatment)) val = null;
        if (val !== null) {
            this.model.sliders[i].value = val;
            this.view.drawSlider(i, {dragged: true});
        }
    }

    dropHandle(event) {
        let i = this.picked_slider;
        this.view.drawSlider(i, {});
        this.picked_slider = null;
        this.submitSlider(i);

        this.input_disabled = true;
        window.setTimeout(() => {
            this.input_disabled = false
        }, js_vars.params.retry_delay * 1000);
    }

    endGame() {
        //document.getElementById("form").submit();
    }

    cheat(values) {
        let i = 0, cnt = Object.keys(values).length;
        let timer = window.setInterval(() => {
            this.model.sliders[i].value = values[i];
            this.submitSlider(i);
            i++;
            if (i == cnt) window.clearInterval(timer);
        }, js_vars.params.retry_delay * 1000 + 100);
    }

    simulateAllSlides(max_slides, speed_factor) {
        const sliderKeys = Object.keys(this.model.sliders);
        let i = 0;

        const tryValuesForSlider = (sliderIndex, values, callback) => {
            let j = 0;

            const tryNextValue = () => {
                if (j < values.length) {
                    const slider = this.model.sliders[sliderIndex];
                    slider.value = values[j];
                    this.view.drawSlider(sliderIndex, {dragged: true});
                    this.submitSlider(sliderIndex);

                    j++;
                    setTimeout(tryNextValue, 1400 * speed_factor); // 1.4 second between values
                } else {
                    callback(); // move to next slider
                }
            };

            tryNextValue();
        };

        const simulateNextSlider = () => {
            if (i < max_slides) {
                const sliderIndex = sliderKeys[i];
                const slider = this.model.sliders[sliderIndex];

                let random = slider.target + Math.floor(Math.random() * 31) - 14;
                if (Math.abs(random - slider.target) <= 1) random = slider.target + 2;

                const values = [random, slider.target];
                console.log(values);
                tryValuesForSlider(sliderIndex, values, () => {
                    i++;
                    simulateNextSlider(); // move to next slider after trying all values
                });
            }
        };

        simulateNextSlider();
    }

}

// Example trigger after window load and Controller initialization
window.onload = (event) => {
    const model = new Model();
    const view = new View(model, js_vars.slider_size);
    const ctrl = new Controller(model, view);

    // Run simulation after 0.5 seconds
    if ($("#player_role").val() === "streamer" && ["BOT_NO_PAY_HUMAN", "BOT_PAYS_HUMAN", "BOT_NO_PAY_BOT", "BOT_PAYS_BOT"].includes(js_vars.params.treatment)) {
        const round_number = parseInt($("#round_number").val());
        console.log(round_number);
        let max_slides;
        let speed_factor
        // This values are avgs based on previous experiments Denom and SocCom
        switch (round_number) {
            case 1:
            case 2:
                max_slides = 13;
                speed_factor = 1.154;
                break;
            case 3:
                max_slides = 14;
                speed_factor = 1.071;
                break;
            case 4:
                max_slides = 13;
                speed_factor = 1.154;
                break;
            case 5:
            case 6:
                max_slides = 15;
                speed_factor = 1.000;
                break;
            case 7:
            case 8:
            case 9:
            case 10:
                max_slides = 16;
                speed_factor = 0.938;
                break;
            default:
                console.error("Unknown round number:", round_number);
                break;
        }
        setTimeout(() => ctrl.simulateAllSlides(max_slides, speed_factor), 1500);
    }
};

