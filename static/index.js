document.getElementById('hamburger-menu').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('sidebar-open');
  });
  


 
  
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const selectGenre = document.getElementById("select_genre");
    const selectMusic = document.getElementById("select_music");
    const selectAlbum = document.getElementById("select_album");
    const selectTrack = document.getElementById("select_track");
    const searchResultsDiv = document.getElementById("search-results");
    const songResultDiv = document.getElementById("for-song-results");
    const artistInput = form.elements.artist;
    const trackInput = form.elements.track;
    const playButton = document.getElementById("btn_submit");
    const artistImage = document.getElementById("artist-image");
  
    artistInput.addEventListener("input", () => {
      const artistName = artistInput.value;
  
      fetch("/search", {
        method: "POST",
        body: new URLSearchParams({
          artist: artistName
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            searchResultsDiv.innerHTML = `<p>${data.error}</p>`;
          } else {
            const { name, genres, popularity, images } = data.result;
  
            searchResultsDiv.innerHTML = `
             <!-- <h4>Popularity: ${popularity}</h4>-->
              <h1>${name}</h1>
              <!--<p>Genres: ${genres.join(", ")}</p>-->
              <img src="${images[0].url}" alt="Artist Image" height="200" width="200">
            `;
  
            populateGenres(data.result.genres);
            populateAlbums(data.albums);
          }
        })
        .catch(error => console.error(error));
    });
  
    trackInput.addEventListener("input", () => {
      const trackName = trackInput.value;
    
      fetch("/search", {
        method: "POST",
        body: new URLSearchParams({
          track: trackName
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            songResultDiv.innerHTML = `<p>${data.error}</p>`;
          } else {
            populateTracks(data.tracks);
            
            // İlk track'i otomatik olarak seç
            if (data.tracks.length > 0) {
              selectTrack.selectedIndex = 0;
              const selectedMusic = selectTrack.value;
              clearPreviousSong();
              const audio = document.createElement("audio");
              audio.src = selectedMusic;
              audio.controls = true;
              songResultDiv.appendChild(audio);
            }
          }
        })
        .catch(error => console.error(error));
    });
  
    selectAlbum.addEventListener("change", () => {
      const selectedAlbumId = selectAlbum.value;
  
      fetch(`/albums/${selectedAlbumId}/songs`, {
        method: "GET"
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            searchResultsDiv.innerHTML = `<p>${data.error}</p>`;
          } else {
            populateSongs(data.songs);
          }
        })
        .catch(error => console.error(error));
    });
  
    selectTrack.addEventListener("change", () => {
      const selectedMusic = selectTrack.value;
  
      clearPreviousSong();
      if (selectedMusic) {
        const audio = document.createElement("audio");
        audio.src = selectedMusic;
        audio.controls = true;
        songResultDiv.appendChild(audio);
      }
    });
  
    playButton.addEventListener("click", () => {
      clearPreviousSong();
      const selectedMusic = selectMusic.value;
      const audio = document.createElement("audio");
      audio.src = selectedMusic;
      audio.controls = true;
      songResultDiv.appendChild(audio);
    });
  
    function clearPreviousSong() {
      const audioElements = songResultDiv.getElementsByTagName("audio");
      while (audioElements.length > 0) {
        audioElements[0].parentNode.removeChild(audioElements[0]);
      }
    }
  
    function populateGenres(genres) {
      // Clear previous options
      selectGenre.innerHTML = "";
  
      // Create and append new options
      genres.forEach(genre => {
        const option = document.createElement("option");
        option.text = genre;
        option.value = genre;
        selectGenre.add(option);
      });
    }
  
    function populateAlbums(albums) {
      // Clear previous options
      selectAlbum.innerHTML = "";
  
      // Create and append new options
      albums.forEach(album => {
        const option = document.createElement("option");
        option.text = album.name;
        option.value = album.id;
        selectAlbum.add(option);
      });
  
      // İlk albümü seç
      if (albums.length > 0) {
        const firstAlbumId = albums[0].id;
        selectAlbum.value = firstAlbumId;
  
        fetch(`/albums/${firstAlbumId}/songs`, {
          method: "GET"
        })
          .then(response => response.json())
          .then(data => {
            if (data.error) {
              searchResultsDiv.innerHTML = `<p>${data.error}</p>`;
            } else {
              populateSongs(data.songs);
            }
          })
          .catch(error => console.error(error));
      }
    }
  
    function populateTracks(tracks) {
      // Clear previous options
      selectTrack.innerHTML = "";
  
      // Create and append new options
      tracks.forEach(track => {
        const option = document.createElement("option");
        option.text = track.name;
        option.value = track.preview_url;
        selectTrack.add(option);
      });
    }
  
    function populateSongs(songs) {
      // Clear previous options
      selectMusic.innerHTML = "";
  
      // Create and append new options
      songs.forEach((song) => {
        const option = document.createElement("option");
        option.text = song.name;
        option.value = song.preview_url;
        selectMusic.add(option);
  
      });
    }
  });
  


  
 

  
  
