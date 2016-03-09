
int times = 5;
void setup() {
    int max = 1000;
    if (max / canvas[0] < max / canvas[1]) {
        times = max / canvas[0];
    }
    else {
        times = max / canvas[1];
    }
    size(canvas[0] * times, canvas[1] * times);
    background(180);
    stroke(100);

}

void drawFabric() {
    for (int i = 0; i < pieces.length(); i++) {
        for (int j = 0; j < 4; j++) {
            pieces[i][j] *= times;
        }
        rect(pieces[i][0],pieces[i][1],pieces[i][2],pieces[i][3]);
    }
}
