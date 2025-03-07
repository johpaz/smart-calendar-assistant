const db = require('./database');

function hayConflicto(fecha, horaInicio, horaFin, excludeId = null, callback) {
  const inicioNuevo = new Date(`${fecha}T${horaInicio}`);
  const finNuevo = new Date(`${fecha}T${horaFin}`);

  let query = 'SELECT * FROM eventos WHERE fecha = ?';
  let params = [fecha];
  if (excludeId) {
    query += ' AND id != ?';
    params.push(excludeId);
  }

  db.all(query, params, (err, rows) => {
    if (err) return callback(err);
    const conflicto = rows.some(evento => {
      const inicioExistente = new Date(`${evento.fecha}T${evento.hora_inicio}`);
      const finExistente = new Date(`${evento.fecha}T${evento.hora_fin}`);
      return inicioNuevo < finExistente && finNuevo > inicioExistente;
    });
    callback(null, conflicto);
  });
}

function agendarEvento(nombre, fecha, horaInicio, horaFin, callback) {
  hayConflicto(fecha, horaInicio, horaFin, null, (err, conflicto) => {
    if (err) return callback(err);
    if (conflicto) {
      return callback(null, { status: 'error', mensaje: 'Conflicto de horario detectado.' });
    }
    db.run(
      'INSERT INTO eventos (nombre, fecha, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)',
      [nombre, fecha, horaInicio, horaFin],
      function (err) {
        if (err) return callback(err);
        callback(null, {
          status: 'success',
          mensaje: 'Reunión agendada con éxito.',
          evento: { id: this.lastID, nombre, fecha, hora_inicio: horaInicio, hora_fin: horaFin }
        });
      }
    );
  });
}
function consultarAgenda(fechaInicio, fechaFin, callback) {
    const sql = 'SELECT * FROM eventos WHERE fecha BETWEEN ? AND ?';
    db.all(sql, [fechaInicio, fechaFin], (err, rows) => {
      if (err) return callback(err);
      callback(null, { status: 'success', mensaje: 'Eventos encontrados.', eventos: rows });
    });
  }
  

function editarEvento(id, nombre, fecha, horaInicio, horaFin, callback) {
  hayConflicto(fecha, horaInicio, horaFin, id, (err, conflicto) => {
    if (err) return callback(err);
    if (conflicto) {
      return callback(null, { status: 'error', mensaje: 'Conflicto de horario detectado.' });
    }
    db.run(
      'UPDATE eventos SET nombre = ?, fecha = ?, hora_inicio = ?, hora_fin = ? WHERE id = ?',
      [nombre, fecha, horaInicio, horaFin, id],
      function (err) {
        if (err) return callback(err);
        if (this.changes === 0) return callback(null, { status: 'error', mensaje: 'Evento no encontrado.' });
        callback(null, {
          status: 'success',
          mensaje: 'Evento editado con éxito.',
          evento: { id, nombre, fecha, hora_inicio: horaInicio, hora_fin: horaFin }
        });
      }
    );
  });
}

function borrarEvento(id, callback) {
  db.run('DELETE FROM eventos WHERE id = ?', [id], function (err) {
    if (err) return callback(err);
    if (this.changes === 0) return callback(null, { status: 'error', mensaje: 'Evento no encontrado.' });
    callback(null, { status: 'success', mensaje: 'Evento borrado con éxito.' });
  });
}

module.exports = { agendarEvento, consultarAgenda, editarEvento, borrarEvento };