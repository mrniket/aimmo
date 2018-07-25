import { combineReducers } from 'redux'
import { combineEpics } from 'redux-observable'
import editorReducer, { editorEpics } from './Editor'
import gameReducer, { gameEpics } from './Game'

const rootEpic = combineEpics(
  ...Object.values(editorEpics),
  ...Object.values(gameEpics)
)

const rootReducer = combineReducers({
  editor: editorReducer,
  game: gameReducer
})

export {
  rootEpic,
  rootReducer
}
