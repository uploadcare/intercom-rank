var SETTINGS = {},
    gulp = require('gulp'),
    less = require('gulp-less'),
    runSequence = require('run-sequence'),
    del = require('del'),
    concat = require('gulp-concat');


SETTINGS.SRC_JSX = './src/js/App.jsx';
SETTINGS.SRC_LESS = './src/css/styles.less';
SETTINGS.JS_DEST = './build/js/';
SETTINGS.LESS_DEST = './build/css';
SETTINGS.PATH_ALL = [SETTINGS.SRC_JSX, SETTINGS.SRC_LESS];

gulp.task('vendor', function() {
    // CSS
    gulp.src('./node_modules/bootstrap/less/bootstrap.less')
        .pipe(less())
        .pipe(gulp.dest(SETTINGS.LESS_DEST));

    // Other
    gulp.src('./node_modules/bootstrap/dist/fonts/**')
        .pipe(gulp.dest('./build/fonts'));
});

gulp.task('less', function () {
    return gulp.src(SETTINGS.SRC_LESS)
        .pipe(less())
        .pipe(gulp.dest(SETTINGS.LESS_DEST))
});


gulp.task('clean', del.bind(
  null, ['.tmp', 'build/*', '!build/.git'], {dot: true}
));

gulp.task('watch', function(){
  gulp.watch(SETTINGS.PATH_ALL, ['less']);
});

gulp.task('default', ['clean'], function (cb) {
    runSequence(['vendor', 'less'], cb);
});
